"""A handler for websocket event requests."""

from asyncio import Event
import logging
from typing import Any, Final, Iterable, cast

from .typing import (
    WebSocketScope,
    WebSocketAcceptEvent,
    WebSocketCloseEvent,
    WebSocketDisconnectEvent,
    WebSocketReceiveEvent,
    WebSocketSendEvent,
    ASGIWebSocketReceiveCallable,
    ASGIWebSocketSendCallable
)

from .callbacks import WebSocketMiddlewareCallback
from .errors import WebSocketInternalError
from .middleware import make_middleware_chain
from .request import WebSocketRequest
from .router import WebSocketRouter
from .websocket import WebSocket, WebSocketState


LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


class WebSocketImpl(WebSocket):
    """A concrete WebSocket implementation"""

    def __init__(self, receive: ASGIWebSocketReceiveCallable, send: ASGIWebSocketSendCallable):
        self._receive = receive
        self._send = send
        self._state: WebSocketState = 'connected'
        self._code: int | None = None
        self._reason: str | None = None
        self._close_event = Event()

    async def accept(
            self,
            subprotocol: str | None = None,
            headers: list[tuple[bytes, bytes]] | None = None
    ) -> None:
        accept_event: WebSocketAcceptEvent = {
            'type': 'websocket.accept',
            'subprotocol': subprotocol,
            'headers': headers or []
        }
        LOGGER.debug('Accepting.')
        await self._send(accept_event)
        self._state = 'open'

    async def receive(self) -> bytes | str | None:
        event = await self._receive()
        LOGGER.debug('Received event type "%s".', event['type'])

        if event['type'] == 'websocket.receive':

            receive_event = cast(WebSocketReceiveEvent, event)
            if 'bytes' in receive_event and receive_event['bytes']:
                return receive_event['bytes']
            else:
                return receive_event['text']

        if event['type'] == 'websocket.disconnect':

            disconnect_event = cast(WebSocketDisconnectEvent, event)
            self._mark_closed(
                disconnect_event.get('code', 1000),
                disconnect_event.get('reason')
            )
            return None

        LOGGER.error('Failed to understand event type "%s".', event['type'])
        raise WebSocketInternalError('Unknown type: ' + event['type'])

    async def send(self, content: bytes | str) -> None:
        send_event: WebSocketSendEvent = {
            'type': 'websocket.send'
        }
        if isinstance(content, bytes):
            send_event['bytes'] = content
        else:
            send_event['text'] = content

        LOGGER.debug('Sending event type "%s".', send_event["type"])
        await self._send(send_event)

    async def close(self, code: int = 1000, reason: str | None = None) -> None:
        response: WebSocketCloseEvent = {
            'type': 'websocket.close',
            'code': code
        }
        if reason:
            response['reason'] = reason
        LOGGER.debug('Closing with code %d (%s).', code, reason or "")
        await self._send(response)
        self._mark_closed(code, reason)

    def _mark_closed(self, code: int, reason: str | None) -> None:
        self._code = code
        self._reason = reason
        self._state = 'closed'
        self._close_event.set()

    async def wait_closed(self) -> None:
        await self._close_event.wait()

    @property
    def state(self) -> WebSocketState:
        return self._state

    @property
    def code(self) -> int:
        if self._state != 'closed':
            raise ValueError("The WebSocket is not closed.")
        assert self._code is not None
        return self._code

    @property
    def reason(self) -> str | None:
        if self._state != 'closed':
            raise ValueError("The WebSocket is not closed.")
        return self._reason


class WebSocketInstance:
    """Provides an instance to handle websocket event requests"""

    def __init__(
            self,
            scope: WebSocketScope,
            router: WebSocketRouter,
            middleware: Iterable[WebSocketMiddlewareCallback],
            info: dict[str, Any]
    ) -> None:
        self.scope = scope
        self.info = info

        self.impl: WebSocketImpl | None = None

        # Find the route.
        handler, matches = router.resolve(scope['path'])
        if handler is None:
            raise ValueError(f"No handler for path {scope['path']}")
        self.handler, self.matches = handler, matches

        # Assemble any middleware.
        if middleware:
            self.handler = make_middleware_chain(
                *middleware,
                handler=self.handler
            )

    async def process(
            self,
            receive: ASGIWebSocketReceiveCallable,
            send: ASGIWebSocketSendCallable
    ) -> None:
        event = await receive()
        LOGGER.debug('Received event type "%s".', event['type'])

        if event['type'] == 'websocket.connect':
            self.impl = WebSocketImpl(receive, send)
            await self.handler(
                WebSocketRequest(
                    self.scope,
                    self.info,
                    {},
                    self.matches,
                    self.impl
                )
            )
        elif event['type'] == 'websocket.disconnect':
            disconnect_event = cast(WebSocketDisconnectEvent, event)
            LOGGER.debug(
                "WebSocket disconnected: %s (%s)",
                disconnect_event['code'],
                disconnect_event.get('reason')
            )
        else:
            LOGGER.error(
                'Failed to understand event type "%s".',
                event['type']
            )
            raise WebSocketInternalError(
                f'Unknown request type "{event["type"]}'
            )

"""A handler for websocket event requests."""

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
from .websocket import WebSocket

LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


class WebSocketImpl(WebSocket):
    """A concrete WebSocket implementation"""

    def __init__(self, receive: ASGIWebSocketReceiveCallable, send: ASGIWebSocketSendCallable):
        self._receive = receive
        self._send = send
        self._code: int | None = None

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
            self._code = disconnect_event.get('code', 1000)
            return None

        LOGGER.error('Failed to understand event type "%s".', event['type'])
        raise WebSocketInternalError('Unknown type: ' + event['type'])

    async def send(self, content: bytes | str) -> None:
        send_event: WebSocketSendEvent = {
            'type': 'websocket.send',
            'bytes': content if isinstance(content, bytes) else None,
            'text': content if isinstance(content, str) else None
        }

        LOGGER.debug('Sending event type "%s".', send_event["type"])
        await self._send(send_event)

    async def close(self, code: int = 1000) -> None:
        response: WebSocketCloseEvent = {
            'type': 'websocket.close',
            'code': code
        }
        LOGGER.debug('Closing with code %d.', code)
        await self._send(response)

    @property
    def code(self) -> str | None:
        """The code return on close

        Returns:
            str | None: The close code
        """
        return "self._code"


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
            await self.handler(
                WebSocketRequest(
                    self.scope,
                    self.info,
                    {},
                    self.matches,
                    WebSocketImpl(receive, send)
                )
            )
        elif event['type'] == 'websocket.disconnect':
            pass
        else:
            LOGGER.error(
                'Failed to understand event type "%s".',
                event['type']
            )
            raise WebSocketInternalError(
                f'Unknown request type "{event["type"]}'
            )

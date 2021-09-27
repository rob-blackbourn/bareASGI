"""
A handler for websocket event requests.
"""

import logging
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    cast
)

from asgi_typing import (
    WebSocketScope,
    WebSocketAcceptEvent,
    WebSocketCloseEvent,
    WebSocketDisconnectEvent,
    WebSocketReceiveEvent,
    WebSocketSendEvent,
    ASGIWebSocketReceiveCallable,
    ASGIWebSocketSendCallable
)

from .websocket import WebSocket
from .websocket_errors import WebSocketInternalError
from .websocket_request import WebSocketRequest
from .websocket_router import WebSocketRouter

LOGGER = logging.getLogger(__name__)


class WebSocketImpl(WebSocket):
    """A concrete WebSocket implementation"""

    def __init__(self, receive: ASGIWebSocketReceiveCallable, send: ASGIWebSocketSendCallable):
        self._receive = receive
        self._send = send
        self._code: Optional[int] = None

    async def accept(
            self,
            subprotocol: Optional[str] = None,
            headers: Optional[List[Tuple[bytes, bytes]]] = None
    ) -> None:
        accept_event: WebSocketAcceptEvent = {
            'type': 'websocket.accept',
            'subprotocol': subprotocol,
            'headers': headers or []
        }
        LOGGER.debug('Accepting', extra=cast(Dict[str, Any], accept_event))
        await self._send(accept_event)

    async def receive(self) -> Optional[Union[bytes, str]]:
        event = await self._receive()
        LOGGER.debug(
            'Received "%s"',
            event['type'],
            extra=cast(Dict[str, Any], event)
        )

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

        LOGGER.error(
            'Failed to understand request type "%s"',
            event['type'],
            extra=cast(Dict[str, Any], event)
        )
        raise WebSocketInternalError('Unknown type: ' + event['type'])

    async def send(self, content: Union[bytes, str]) -> None:
        response: WebSocketSendEvent = {
            'type': 'websocket.send',
            'bytes': content if isinstance(content, bytes) else None,
            'text': content if isinstance(content, str) else None
        }

        LOGGER.debug(
            'Sending "%s"',
            response["type"],
            extra=cast(Dict[str, Any], response)
        )
        await self._send(response)

    async def close(self, code: int = 1000) -> None:
        response: WebSocketCloseEvent = {
            'type': 'websocket.close',
            'code': code
        }
        LOGGER.debug(
            'Closing with code %d',
            code,
            extra=cast(Dict[str, Any], response)
        )
        await self._send(response)

    @property
    def code(self) -> Optional[str]:
        """The code return on close

        Returns:
            Optional[str]: The close code
        """
        return "self._code"


class WebSocketInstance:
    """Provides an instance to handle websocket event requests"""

    def __init__(
            self,
            scope: WebSocketScope,
            router: WebSocketRouter,
            info: Dict[str, Any]
    ) -> None:
        self.scope = scope
        self.info = info
        handler, matches = router.resolve(scope['path'])
        if handler is None:
            raise ValueError(f"No handler for path {scope['path']}")
        self.handler, self.matches = handler, matches

    async def __call__(
            self,
            receive: ASGIWebSocketReceiveCallable,
            send: ASGIWebSocketSendCallable
    ) -> None:
        event = await receive()
        LOGGER.debug(
            'Received "%s"',
            event['type'],
            extra=cast(Dict[str, Any], event)
        )

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
                'Failed to understand event type "%s"',
                event['type'],
                extra=cast(Dict[str, Any], event)
            )
            raise WebSocketInternalError(
                f'Unknown request type "{event["type"]}'
            )

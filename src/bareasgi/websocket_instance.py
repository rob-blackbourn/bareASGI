"""
A handler for websocket event requests.
"""
from typing import Optional, Union
import logging
from baretypes import (
    Scope,
    Info,
    Send,
    Receive,
    WebSocket,
    WebSocketRouter,
    WebSocketInternalError
)

logger = logging.getLogger(__name__)


class WebSocketImpl(WebSocket):
    """A concrete WebSocket implementation"""

    def __init__(self, receive: Receive, send: Send):
        self._receive = receive
        self._send = send

    async def accept(self, subprotocol: Optional[str] = None) -> None:
        response = {'type': 'websocket.accept'}
        if subprotocol:
            response['subprotocol'] = subprotocol
        logger.debug('Accepting', extra=response)
        await self._send(response)

    async def receive(self) -> Optional[Union[bytes, str]]:
        request = await self._receive()
        request_type = request['type']
        logger.debug('Received "%s"', request_type, extra=request)

        if request_type == 'websocket.receive':
            return request['bytes'] if 'bytes' in request and request['bytes'] else request['text']
        if request_type == 'websocket.disconnect':
            return None

        logger.error('Failed to understand request type "%s"', request_type, extra=request)
        raise WebSocketInternalError(f'Unknown type: "{request_type}"')

    async def send(self, content: Union[bytes, str]) -> None:
        response = {'type': 'websocket.send'}

        if isinstance(content, bytes):
            response['bytes'] = content
        elif isinstance(content, str):
            response['text'] = content
        else:
            raise ValueError('Content must be bytes or str')

        logger.debug('Sending "%s"', response["type"], extra=response)
        await self._send(response)

    async def close(self, code: int = 1000) -> None:
        response = {'type': 'websocket.close', 'code': code}
        logger.debug('Closing with code %d', code, extra=response)
        await self._send(response)


# pylint: disable=too-few-public-methods
class WebSocketInstance:
    """Provides an instance to handle websocket event requests"""

    def __init__(self, scope: Scope, web_socker_router: WebSocketRouter, info: Info) -> None:
        self.scope = scope
        self.info = info
        self.request_handler, self.matches = web_socker_router.resolve(scope['path'])

    async def __call__(self, receive: Receive, send: Send):

        request = await receive()
        request_type = request['type']
        logger.debug('Received "%s"', request_type, extra=request)

        if request_type == 'websocket.connect':
            await self.request_handler(
                self.scope,
                self.info,
                self.matches,
                WebSocketImpl(receive, send)
            )
        elif request_type == 'websocket.disconnect':
            pass
        else:
            logger.error('Failed to understand request type "%s"', request_type, extra=request)
            raise WebSocketInternalError(f'Unknown request type "{request_type}')

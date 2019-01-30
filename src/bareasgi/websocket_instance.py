from typing import Optional, Union
import logging
from .types import (
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
        logger.debug(f'Received {request_type}', extra=request)

        if request_type == 'websocket.receive':
            return request['bytes'] if 'bytes' in request and request['bytes'] else request['text']
        elif request_type == 'websocket.disconnect':
            return None

        logger.error(f'Failed to understand request type "{request_type}', extra=request)
        raise WebSocketInternalError(f'Unknown type: "{request_type}"')


    async def send(self, content: Union[bytes, str]) -> None:
        response = {'type': 'websocket.send'}

        if isinstance(content, bytes):
            response['bytes'] = content
        elif isinstance(content, str):
            response['text'] = content
        else:
            raise ValueError('Content must be bytes or str')

        logger.debug(f'Sending {response["type"]}', extra=response)
        await self._send(response)


    async def close(self, code: int = 1000) -> None:
        response = {'type': 'websocket.close', 'code': code}
        logger.debug(f'Closing with code {code}', extra=response)
        await self._send(response)


class WebSocketInstance:

    def __init__(self, scope: Scope, route_handler: WebSocketRouter, info: Optional[Info] = None) -> None:
        self.scope = scope
        self.info = info or {}
        self.request_handler, self.matches = route_handler(scope)


    async def __call__(self, receive: Receive, send: Send):

        request = await receive()
        request_type = request['type']
        logger.debug(f'Received {request_type}', extra=request)

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
            logger.error(f'Failed to understand request type "{request_type}', extra=request)
            raise WebSocketInternalError(f'Unknown request type "{request_type}')

"""
A handler for websocket event requests.
"""

import logging
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union
)

from baretypes import (
    Scope,
    Info,
    Header,
    Send,
    Receive,
    WebSocket,
    WebSocketRouter,
    WebSocketInternalError
)

LOGGER = logging.getLogger(__name__)


class WebSocketImpl(WebSocket):
    """A concrete WebSocket implementation"""

    def __init__(self, receive: Receive, send: Send):
        self._receive = receive
        self._send = send
        self._code: Optional[int] = None

    async def accept(
            self,
            subprotocol: Optional[str] = None,
            headers: Optional[List[Header]] = None
    ) -> None:
        response: Dict[str, Any] = {'type': 'websocket.accept'}
        if subprotocol:
            response['subprotocol'] = subprotocol
        if headers:
            response['headers'] = headers
        LOGGER.debug('Accepting', extra=response)
        await self._send(response)

    async def receive(self) -> Optional[Union[bytes, str]]:
        request = await self._receive()
        request_type = request['type']
        LOGGER.debug('Received "%s"', request_type, extra=request)

        if request_type == 'websocket.receive':
            return request['bytes'] if 'bytes' in request and request['bytes'] else request['text']
        if request_type == 'websocket.disconnect':
            self._code = request.get('code', 1000)
            return None

        LOGGER.error('Failed to understand request type "%s"',
                     request_type, extra=request)
        raise WebSocketInternalError(f'Unknown type: "{request_type}"')

    async def send(self, content: Union[bytes, str]) -> None:
        response: Dict[str, Any] = {'type': 'websocket.send'}

        if isinstance(content, bytes):
            response['bytes'] = content
        elif isinstance(content, str):
            response['text'] = content
        else:
            raise ValueError('Content must be bytes or str')

        LOGGER.debug('Sending "%s"', response["type"], extra=response)
        await self._send(response)

    async def close(self, code: int = 1000) -> None:
        response = {'type': 'websocket.close', 'code': code}
        LOGGER.debug('Closing with code %d', code, extra=response)
        await self._send(response)

    @property
    def code(self) -> Optional[str]:
        """The code return on close

        :return: [description]
        :rtype: The close code
        """
        return "self._code"

# pylint: disable=too-few-public-methods


class WebSocketInstance:
    """Provides an instance to handle websocket event requests"""

    def __init__(self, scope: Scope, web_socket_router: WebSocketRouter, info: Info) -> None:
        self.scope = scope
        self.info = info
        self.request_handler, self.matches = web_socket_router.resolve(
            scope['path'])

    async def __call__(self, receive: Receive, send: Send):

        request = await receive()
        request_type = request['type']
        LOGGER.debug('Received "%s"', request_type, extra=request)

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
            LOGGER.error('Failed to understand request type "%s"',
                         request_type, extra=request)
            raise WebSocketInternalError(
                f'Unknown request type "{request_type}')

from typing import Optional, Union
from .types import (
    Scope,
    Info,
    Send,
    Receive,
    WebSocket,
    WebSocketRouter
)


class WebSocketImpl(WebSocket):

    def __init__(self, receive: Receive, send: Send):
        self._receive = receive
        self._send = send


    async def accept(self, subprotocol: Optional[str] = None) -> None:
        response = {'type': 'websocket.accept'}
        if subprotocol:
            response['subprotocol'] = subprotocol
        await self._send(response)


    async def receive(self) -> Optional[Union[bytes, str]]:
        request = await self._receive()

        if request['type'] == 'websocket.receive':
            return request['bytes'] if 'bytes' in request and request['bytes'] else request['text']
        elif request['type'] == 'websocket.disconnect':
            return None
        raise Exception(f"Unknown type: '{request['type']}'")


    async def send(self, content: Union[bytes, str]) -> None:
        response = {'type': 'websocket.send'}
        if isinstance(content, bytes):
            response['bytes'] = content
        elif isinstance(content, str):
            response['text'] = content
        else:
            raise Exception('Content must be bytes or str')
        await self._send(response)


    async def close(self, code: int = 1000) -> None:
        await self._send({'type': 'websocket.close', 'code': code})


class WebSocketInstance:

    def __init__(self, scope: Scope, route_handler: WebSocketRouter, info: Optional[Info] = None) -> None:
        self.scope = scope
        self.info = info or {}
        self.request_handler, self.matches = route_handler(scope)


    async def __call__(self, receive: Receive, send: Send):

        # Fetch the request
        request = await receive()

        if request['type'] == 'websocket.connect':
            await self.request_handler(
                self.scope,
                self.info,
                self.matches,
                WebSocketImpl(receive, send)
            )
        elif request['type'] == 'websocket.disconnect':
            pass

from __future__ import annotations
from typing import Optional, Union
from .types import (
    Scope,
    Context,
    Info,
    Send,
    Receive,
    WebRequest,
    RouteHandler
)


class WebSocket:

    def __init__(self, receive: Receive, send: Send):
        self.receive = receive
        self.send = send


    async def accept(self, subprotocol: Optional[str]) -> None:
        response = {'type': 'websocket.accept'}
        if subprotocol:
            response['subprotocol'] = subprotocol
        await self.send(response)


    async def receive(self) -> Optional[Union[bytes, str]]:
        request = await self.receive()

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
        await self.send(response)


    async def close(self, code: int = 1000) -> None:
        await self.send({'type': 'websocket.close', 'code': code})


class WebSocketRequest(WebRequest):

    def __init__(self, scope: Scope, web_socket: WebSocket) -> None:
        super().__init__(scope)
        self.web_socket = web_socket


class WebSocketInstance:

    def __init__(self, scope: Scope, context: Optional[Context] = None, info: Optional[Info] = None) -> None:
        self.scope = scope
        self.context = context or {}
        self.info = info or {}
        route_handler: RouteHandler = self.context['websocket.connect']
        self.request_handler, self.matches = route_handler(scope)


    async def __call__(self, receive: Receive, send: Send):

        # Fetch the request
        request = await receive()

        if request['type'] == 'websocket.connect':
            await self.request_handler(
                WebSocketRequest(
                    self.scope,
                    WebSocket(receive, send)
                )
            )
        elif request['type'] == 'websocket.disconnect':
            pass

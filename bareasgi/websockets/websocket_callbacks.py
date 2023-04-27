"""The WebSocket callbacks"""

from typing import Awaitable, Callable

from .websocket_request import WebSocketRequest

WebSocketRequestCallback = Callable[
    [WebSocketRequest],
    Awaitable[None]
]
WebSocketMiddlewareCallback = Callable[
    [WebSocketRequest, WebSocketRequestCallback],
    Awaitable[None]
]

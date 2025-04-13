"""The WebSocket callbacks"""

from typing import Awaitable, Callable

from .request import WebSocketRequest

WebSocketRequestCallback = Callable[
    [WebSocketRequest],
    Awaitable[None]
]
WebSocketMiddlewareCallback = Callable[
    [WebSocketRequest, WebSocketRequestCallback],
    Awaitable[None]
]

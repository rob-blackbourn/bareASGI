"""The WebSocket callbacks"""

from typing import Awaitable, Callable

from .request import WebSocketRequest

type WebSocketRequestCallback = Callable[
    [WebSocketRequest],
    Awaitable[None]
]
type WebSocketMiddlewareCallback = Callable[
    [WebSocketRequest, WebSocketRequestCallback],
    Awaitable[None]
]

type WebSocketMiddlewares = list[WebSocketMiddlewareCallback]

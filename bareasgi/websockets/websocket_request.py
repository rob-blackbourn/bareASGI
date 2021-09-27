"""The websocket request"""

from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Mapping,
)

from asgi_typing import WebSocketScope

from .websocket import WebSocket


class WebSocketRequest:

    def __init__(
            self,
            scope: WebSocketScope,
            info: Dict[str, Any],
            context: Dict[str, Any],
            matches: Mapping[str, Any],
            web_socket: WebSocket
    ) -> None:
        self.scope = scope
        self.info = info
        self.context = context
        self.matches = matches
        self.web_socket = web_socket


WebSocketRequestCallback = Callable[
    [WebSocketRequest],
    Awaitable[None]
]

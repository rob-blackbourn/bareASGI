"""The websocket request"""

from typing import Any, Mapping

from .typing import WebSocketScope

from .websocket import WebSocket


class WebSocketRequest:
    """A WebSocket request"""

    def __init__(
            self,
            scope: WebSocketScope,
            info: dict[str, Any],
            context: dict[str, Any],
            matches: Mapping[str, Any],
            web_socket: WebSocket
    ) -> None:
        """A WebSocket request.

        Args:
            scope (WebSocketScope): The ASGI WebSocket scope.
            info (Dict[str, Any]): The shared information from the Application.
            context (Dict[str, Any]): The private information for this request or chain of requests.
            matches (Mapping[str, Any]): Any path matches from the router.
            web_socket (WebSocket): The WebSocket.
        """
        self.scope = scope
        self.info = info
        self.context = context
        self.matches = matches
        self.web_socket = web_socket

"""The abstract class for a websocket router"""

from abc import ABCMeta, abstractmethod
from typing import Any, Mapping, Tuple

from .websocket_request import WebSocketRequestCallback


class WebSocketRouter(metaclass=ABCMeta):
    """The interface for a WebSocket router"""

    @abstractmethod
    def add(
            self,
            path: str,
            callback: WebSocketRequestCallback
    ) -> None:
        """Add the WebSocket handler for a route

        Args:
            path (str): The path.
            callback (WebSocketRequestCallback): The handler
        """

    @abstractmethod
    def resolve(
            self,
            path: str
    ) -> Tuple[WebSocketRequestCallback, Mapping[str, Any]]:
        """Resolve a route to a handler

        Args:
            path (str): The path

        Returns:
            Tuple[WebSocketRequestCallback, Mapping[str, Any]]: A handler and the
                route matches
        """

"""
A basic Websocket router.
"""

from typing import Any, Tuple, List, Mapping
import logging

from ..websockets import WebSocketRouter, WebSocketRequestCallback

from .path_definition import PathDefinition

LOGGER = logging.getLogger(__name__)

Route = Tuple[PathDefinition, WebSocketRequestCallback]


class BasicWebSocketRouter(WebSocketRouter):
    """The implementation of a basic Websocket router"""

    def __init__(self) -> None:
        self._routes: List[Route] = []

    def add(self, path: str, callback: WebSocketRequestCallback) -> None:
        self._routes.append((PathDefinition(path), callback))

    def resolve(
            self,
            path: str
    ) -> Tuple[WebSocketRequestCallback, Mapping[str, Any]]:
        for path_definition, handler in self._routes:
            is_match, matches = path_definition.match(path)
            if is_match:
                LOGGER.debug(
                    'Matched "%s"" with %s',
                    path,
                    path_definition,
                    extra={'path': path}
                )
                return handler, matches

        LOGGER.warning(
            'Failed to find a match for "%s"',
            path,
            extra={'path': path}
        )

        # TODO: Should we have a "route not found" handler?
        raise ValueError(f"Unable to find route for {path}")

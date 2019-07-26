from typing import Optional, Tuple, List
import logging
from baretypes import WebSocketRouter, RouteMatches, WebSocketRequestCallback
from .path_definition import PathDefinition

logger = logging.getLogger(__name__)


class BasicWebSocketRouter(WebSocketRouter):

    def __init__(self) -> None:
        self._routes: List[Tuple[PathDefinition, WebSocketRequestCallback]] = []

    def add(self, path: str, callback: WebSocketRequestCallback) -> None:
        self._routes.append((PathDefinition(path), callback))

    def resolve(self, path: str) -> Tuple[Optional[WebSocketRequestCallback], Optional[RouteMatches]]:
        for path_definition, handler in self._routes:
            is_match, matches = path_definition.match(path)
            if is_match:
                logger.debug(f'Matched "{path} with {path_definition}', extra={'path': path})
                return handler, matches

        logger.warning(f'Failed to find a match for "{path}', extra={'path': path})

        # TODO: Should we have a "route not found" handler?
        return None, None

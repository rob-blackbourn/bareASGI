from typing import Optional, Tuple, List
import logging
from ..types import WebSocketRouter, RouteMatches, Scope
from ..types import WebSocketRequestCallback
from .path_definition import PathDefinition

logger = logging.getLogger(__name__)


class BasicWebSocketRouter(WebSocketRouter):

    def __init__(self) -> None:
        self._routes: List[Tuple[PathDefinition, WebSocketRequestCallback]] = []


    def add(self, path: str, callback: WebSocketRequestCallback) -> None:
        self._routes.append((PathDefinition(path), callback))


    def __call__(self, scope: Scope) -> Tuple[Optional[WebSocketRequestCallback], Optional[RouteMatches]]:
        for path_definition, handler in self._routes:
            is_match, matches = path_definition.match(scope['path'])
            if is_match:
                logger.debug(f'Matched "{scope["path"]} with {path_definition}', extra=scope)
                return handler, matches

        logger.warning(f'Failed to find a match for "{scope["path"]}', extra=scope)
        # TODO: Should we have a "route not found" handler?
        return None, None

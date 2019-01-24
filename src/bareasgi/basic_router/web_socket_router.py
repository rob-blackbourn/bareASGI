from typing import Optional, Tuple, List
from ..types import WebSocketRouter, RouteMatches, Scope
from ..types import WebSocketRequestCallback
from .path_definition import PathDefinition


class BasicWebSocketRouter(WebSocketRouter):

    def __init__(self) -> None:
        self._routes: List[Tuple[PathDefinition, WebSocketRequestCallback]] = []


    def add(self, path: str, callback: WebSocketRequestCallback) -> None:
        self._routes.append((PathDefinition(path), callback))


    def __call__(self, scope: Scope) -> Tuple[Optional[WebSocketRequestCallback], Optional[RouteMatches]]:
        for path_definition, handler in self._routes:
            is_match, matches = path_definition.match(scope['path'])
            if is_match:
                return handler, matches
        return None, None

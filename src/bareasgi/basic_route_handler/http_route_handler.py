from typing import AbstractSet, Optional, Tuple
from ..types import HttpRouteHandler, RouteMatches, Scope
from ..types import HttpRequestCallback
from .path_definition import PathDefinition


class BasicHttpRouteHandler(HttpRouteHandler):

    def __init__(self) -> None:
        self._routes = {}


    def add(self, methods: AbstractSet[str], path: str, callback: HttpRequestCallback) -> None:
        for method in methods:
            path_definition_list = self._routes.setdefault(method, [])
            path_definition_list.append((PathDefinition(path), callback))


    def __call__(self, scope: Scope) -> Tuple[Optional[HttpRequestCallback], Optional[RouteMatches]]:
        path_definition_list = self._routes.get(scope['method'])
        if path_definition_list:
            for path_definition, handler in path_definition_list:
                is_match, matches = path_definition.match(scope['path'])
                if is_match:
                    return handler, matches
        return None, None

from typing import AbstractSet, Optional, Tuple
from ..types import (
    HttpRouter,
    RouteMatches,
    Scope,
    Info,
    Content,
    HttpResponse,
    HttpRequestCallback
)
from .path_definition import PathDefinition


class BasicHttpRouter(HttpRouter):

    def __init__(self, not_found_response: HttpResponse) -> None:
        self._routes = {}
        self._not_found_response = not_found_response


    @property
    def not_found_response(self):
        return self._not_found_response


    @not_found_response.setter
    def not_found_response(self, value: HttpResponse):
        self._not_found_response = value


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


        async def not_found(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
            return self._not_found_response


        return not_found, {}

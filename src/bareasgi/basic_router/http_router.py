from typing import AbstractSet, Optional, Tuple
import logging
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

logger = logging.getLogger(__name__)


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
        logger.debug(f'Adding route for {methods} on "{path}"')
        for method in methods:
            path_definition_list = self._routes.setdefault(method, [])
            path_definition_list.append((PathDefinition(path), callback))


    async def _not_found(self, scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
        return self._not_found_response


    def __call__(self, scope: Scope) -> Tuple[Optional[HttpRequestCallback], Optional[RouteMatches]]:
        path_definition_list = self._routes.get(scope['method'])
        if path_definition_list:
            for path_definition, handler in path_definition_list:
                is_match, matches = path_definition.match(scope['path'])
                if is_match:
                    logger.debug(
                        f'Matched {scope["method"]} on "{scope["path"]}" for {path_definition} matching {matches}',
                        extra=scope)
                    return handler, matches

        logger.warning(f'Failed to find a match for {scope["method"]} on "{scope["path"]}"', extra=scope)
        return self._not_found, {}

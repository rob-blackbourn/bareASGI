"""
Http Routing
"""

import logging
from typing import (
    AbstractSet,
    Dict,
    List,
    Tuple
)

from ..types import (
    HttpRouter,
    RouteMatches,
    HttpRequest,
    HttpResponse,
    HttpRequestCallback
)

from .path_definition import PathDefinition

LOGGER = logging.getLogger(__name__)

Route = Tuple[PathDefinition, HttpRequestCallback]


class BasicHttpRouter(HttpRouter):
    """A basic http routing implementation"""

    def __init__(self, not_found_response: HttpResponse) -> None:
        self._routes: Dict[str, List[Route]] = {}
        self._not_found_response = not_found_response

    @property
    def not_found_response(self) -> HttpResponse:
        return self._not_found_response

    @not_found_response.setter
    def not_found_response(self, value: HttpResponse) -> None:
        self._not_found_response = value

    def add(
            self,
            methods: AbstractSet[str],
            path: str,
            callback: HttpRequestCallback
    ) -> None:
        LOGGER.debug('Adding route for %s on "%s"', methods, path)
        path_definition = PathDefinition(path)
        for method in methods:
            self.add_route(method, path_definition, callback)

    def add_route(
            self,
            method: str,
            path_definition: PathDefinition,
            callback: HttpRequestCallback
    ) -> None:
        """Add a route to a callback for a method and path definition

        Args:
            method (str): The method.
            path_definition (PathDefinition): The path definition
            callback (HttpRequestCallback): The callback
        """
        path_definition_list = self._routes.setdefault(method, [])
        path_definition_list.append((path_definition, callback))

    # pylint: disable=unused-argument
    async def _not_found(
            self,
            request: HttpRequest
    ) -> HttpResponse:
        return self._not_found_response

    def resolve(
            self,
            method: str,
            path: str
    ) -> Tuple[HttpRequestCallback, RouteMatches]:
        path_definition_list = self._routes.get(method)
        if path_definition_list:
            for path_definition, handler in path_definition_list:
                is_match, matches = path_definition.match(path)
                if is_match:
                    LOGGER.debug(
                        'Matched %s on "%s" for %s matching %s',
                        method,
                        path,
                        path_definition,
                        matches,
                        extra={'method': method, 'path': path}
                    )
                    return handler, matches

        LOGGER.warning(
            'Failed to find a match for %s on "%s"',
            method,
            path,
            extra={'method': method, 'path': path}
        )
        return self._not_found, {}

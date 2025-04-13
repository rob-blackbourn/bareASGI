"""The abstract class for http routing"""

from abc import ABCMeta, abstractmethod
from typing import Any, Mapping

from .callbacks import HttpRequestCallback
from .response import HttpResponse


class HttpRouter(metaclass=ABCMeta):
    """The interface for an HTTP router"""

    @property  # type: ignore
    @abstractmethod
    def not_found_response(self) -> HttpResponse:
        """The response when a handler could not be found for a method/path

        Returns:
            HttpResponse: The response when a route cannot be found.
        """

    @not_found_response.setter  # type: ignore
    @abstractmethod
    def not_found_response(self, value: HttpResponse) -> None:
        ...

    @abstractmethod
    def add(
            self,
            methods: set[str],
            path: str,
            callback: HttpRequestCallback
    ) -> None:
        """Add an HTTP request handler

        Args:
            methods (set[str]): The supported HTTP methods.
            path (str): The path.
            callback (HttpRequestCallback): The request handler.
        """

    @abstractmethod
    def resolve(
            self,
            method: str,
            path: str
    ) -> tuple[HttpRequestCallback, Mapping[str, Any]]:
        """Resolve a request to a handler with the route matches

        Args:
            method (str): The HTTP method.
            path (str): The path.

        Returns:
            Tuple[HttpRequestCallback, Mapping[str, Any]]: A handler and the route
                matches.
        """

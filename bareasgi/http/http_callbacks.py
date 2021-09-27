"""Http callbacks"""

from typing import Awaitable, Callable

from .http_request import HttpRequest
from .http_response import HttpResponse

HttpRequestCallback = Callable[
    [HttpRequest],
    Awaitable[HttpResponse]
]
HttpMiddlewareCallback = Callable[
    [HttpRequest, HttpRequestCallback],
    Awaitable[HttpResponse]
]

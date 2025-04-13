"""The http callbacks"""

from typing import Awaitable, Callable

from .request import HttpRequest
from .response import HttpResponse

HttpRequestCallback = Callable[
    [HttpRequest],
    Awaitable[HttpResponse]
]
HttpMiddlewareCallback = Callable[
    [HttpRequest, HttpRequestCallback],
    Awaitable[HttpResponse]
]

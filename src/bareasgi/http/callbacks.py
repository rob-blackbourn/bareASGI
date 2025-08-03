"""The http callbacks"""

from typing import Awaitable, Callable

from .request import HttpRequest
from .response import HttpResponse

type HttpRequestCallback = Callable[
    [HttpRequest],
    Awaitable[HttpResponse]
]
type HttpMiddlewareCallback = Callable[
    [HttpRequest, HttpRequestCallback],
    Awaitable[HttpResponse]
]

type HttpMiddlewares = list[HttpMiddlewareCallback]

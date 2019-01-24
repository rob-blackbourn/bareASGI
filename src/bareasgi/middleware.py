from functools import partial
from .types import HttpRequestCallback, HttpMiddlewareCallback


def mw(*handlers: HttpMiddlewareCallback, handler: HttpRequestCallback) -> HttpRequestCallback:

    for middleware in reversed(handlers):
        handler = partial(middleware, handler=handler)
    return handler

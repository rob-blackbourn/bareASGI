from functools import partial
from .types import HttpRequestCallback, HttpMiddlewareCallback


def mw(
        *handlers: HttpMiddlewareCallback,
        handler: HttpRequestCallback
) -> HttpRequestCallback:
    """Create a handler from a chain of middleware.

    :param handlers: The middleware handlers.
    :param handler: The final response handler.
    :return: A handler which calls the middleware chain.
    """

    for middleware in reversed(handlers):
        handler = partial(middleware, handler=handler)
    return handler

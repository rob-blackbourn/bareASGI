"""The http middleware"""

from functools import partial

from .callbacks import HttpRequestCallback, HttpMiddlewareCallback
from .request import HttpRequest
from .response import HttpResponse


async def _call_handler(
        handler: HttpRequestCallback,
        request: HttpRequest
) -> HttpResponse:
    return await handler(request)


def make_middleware_chain(
        *handlers: HttpMiddlewareCallback,
        handler: HttpRequestCallback
) -> HttpRequestCallback:
    """Create a handler from a chain of middleware.

    Args:
        *handlers (HttpMiddlewareCallback): The middleware handlers.
        handler (HttpRequestCallback): The final response handler.

    Returns:
        HttpRequestCallback: A handler which calls the middleware chain.
    """
    for middleware in reversed(handlers):
        nested_handler = partial(_call_handler, handler)
        handler = partial(middleware, handler=nested_handler)  # type: ignore
    return handler

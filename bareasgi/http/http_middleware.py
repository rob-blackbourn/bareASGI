"""The http middleware"""

from functools import partial

from .http_callbacks import HttpRequestCallback, HttpMiddlewareCallback
from .http_request import HttpRequest
from .http_response import HttpResponse


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
        handler = partial(middleware, handler=partial(_call_handler, handler))
    return handler

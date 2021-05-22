"""
Middleware utilities.
"""

from functools import partial
from typing import Optional

from baretypes import (
    HttpRequestCallback,
    HttpMiddlewareCallback,
    HttpFullResponse,
    Headers,
    Content,
    PushResponses,
    Scope,
    Info,
    RouteMatches
)


def _unpack_response(
        status: int,
        headers: Optional[Headers] = None,
        content: Optional[Content] = None,
        pushes: Optional[PushResponses] = None
) -> HttpFullResponse:
    return status, headers, content, pushes


async def _call_handler(
        handler: HttpRequestCallback,
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpFullResponse:
    response = await handler(scope, info, matches, content)
    if not isinstance(response, tuple):
        response = (response,)
    return _unpack_response(*response)


# pylint: disable=invalid-name
def mw(
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

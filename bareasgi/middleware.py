"""
Middleware utilities.
"""

from functools import partial
from typing import Optional, Tuple

from baretypes import (
    HttpRequestCallback,
    HttpMiddlewareCallback,
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
) -> Tuple[int, Headers, Content, PushResponses]:
    return status, headers, content, pushes


async def _call_handler(
        handler: HttpRequestCallback,
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> Tuple[int, Headers, Content, PushResponses]:
    response = await handler(scope, info, matches, content)
    if isinstance(response, int):
        response = (response,)
    return _unpack_response(*response)


# pylint: disable=invalid-name
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
        handler = partial(middleware, handler=partial(_call_handler, handler))
    return handler

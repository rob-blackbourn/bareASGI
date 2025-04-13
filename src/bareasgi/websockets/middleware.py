"""The WebSocket middleware"""

from functools import partial

from .callbacks import (
    WebSocketRequestCallback,
    WebSocketMiddlewareCallback
)
from .request import WebSocketRequest


async def _call_handler(
        handler: WebSocketRequestCallback,
        request: WebSocketRequest
) -> None:
    await handler(request)


def make_middleware_chain(
        *handlers: WebSocketMiddlewareCallback,
        handler: WebSocketRequestCallback
) -> WebSocketRequestCallback:
    """Create a handler from a chain of middleware.

    Args:
        *handlers (WebSocketMiddlewareCallback): The middleware handlers.
        handler (WebSocketRequestCallback): The final response handler.

    Returns:
        WebSocketRequestCallback: A handler which calls the middleware chain.
    """
    for middleware in reversed(handlers):
        handler = partial(middleware, handler=partial(_call_handler, handler))
    return handler

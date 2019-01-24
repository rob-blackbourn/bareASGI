from typing import Generator, List
from functools import partial
from .types import HttpRequestCallback

def _prepare_middleware(middlewares):
    for middleware in middlewares:
        yield middleware


def _make_middleware_handler(middleware, handler):
    async def invoke(request):
        return await middleware(request, handler)
    return invoke


def mw(*handlers) -> HttpRequestCallback:

    reverse_handlers = reversed(handlers)
    handler = next(reverse_handlers)
    for middleware in _prepare_middleware(reverse_handlers):
        handler = partial(middleware, handler=handler)
    return handler

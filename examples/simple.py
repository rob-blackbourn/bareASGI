"""
A simple request handler.
"""

import logging

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)


async def http_request_callback(
        _scope: Scope,
        _info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    """A request handler which returns some text"""
    return 200, [(b'content-type', b'text/plain')], text_writer('This is not a test')


if __name__ == "__main__":
    import uvicorn

    app = Application()
    app.http_router.add({'GET'}, '/{rest:path}', http_request_callback)

    uvicorn.run(app, port=9009)

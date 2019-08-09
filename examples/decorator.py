"""
A simple request handler.
"""
import logging

import uvicorn

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    Message,
    HttpResponse,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)

app = Application()

# pylint: disable=unused-argument
@app.on_startup
async def my_startup_handler(scope: Scope, info: Info, message: Message) -> None:
    """A startup handler"""
    print('Starting up')

# pylint: disable=unused-argument
@app.on_shutdown
async def my_shutdown_handler(scope: Scope, info: Info, message: Message) -> None:
    """A shutdown handler"""
    print('Shutting down')

# pylint: disable=unused-argument
@app.on_http_request({'GET'}, '/{rest:path}')
async def http_request_callback(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A request handler which returns some text"""
    return 200, [(b'content-type', b'text/plain')], text_writer('This is not a test')

uvicorn.run(app, port=9009)

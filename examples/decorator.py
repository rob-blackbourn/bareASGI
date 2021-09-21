"""
A simple request handler.
"""

import logging

import uvicorn

from bareasgi import (
    Application,
    Scope,
    Info,
    Message,
    HttpRequest,
    HttpResponse,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)

app = Application()


@app.on_startup
async def my_startup_handler(_scope: Scope, _info: Info, _message: Message) -> None:
    """A startup handler"""
    print('Starting up')


@app.on_shutdown
async def my_shutdown_handler(_scope: Scope, _info: Info, _message: Message) -> None:
    """A shutdown handler"""
    print('Shutting down')


@app.on_http_request({'GET'}, '/{rest:path}')
async def http_request_callback(_request: HttpRequest) -> HttpResponse:
    """A request handler which returns some text"""
    return HttpResponse(
        200,
        [(b'content-type', b'text/plain')],
        text_writer('This is not a test')
    )

uvicorn.run(app, port=9009)

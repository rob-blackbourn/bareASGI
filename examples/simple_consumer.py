"""
A simple request handler that consumes content.
"""

import asyncio
import os
import socket

from hypercorn.asyncio import serve
from hypercorn.config import Config

from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    Scope,
    Info,
    RouteMatches,
    Content
)
from bareutils import response_code, text_writer
from bareutils.compression import make_default_compression_middleware

# logging.basicConfig(level=logging.DEBUG)


async def http_request_callback(request: HttpRequest) -> HttpResponse:
    """consume content"""
    async for item in request.body:
        print(item)
    headers = [(b'content-type', b'text/plain')]
    return HttpResponse(
        response_code.OK,
        headers,
        text_writer('THis is not a test')
    )


if __name__ == "__main__":
    compression_middleware = make_default_compression_middleware(
        minimum_size=1024)

    app = Application(middlewares=[compression_middleware])
    app.http_router.add({'GET'}, '/consume', http_request_callback)

    hostname = socket.getfqdn()  # pylint: disable=invalid-name

    config = Config()
    config.bind = [f"{hostname}:9005"]
    config.certfile = os.path.expanduser("~/.keys/server.crt")
    config.keyfile = os.path.expanduser("~/.keys/server.key")
    asyncio.run(serve(app, config))  # type: ignore

"""
A simple request handler.
"""

import logging
import uvicorn

from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)


async def http_request_callback(_request: HttpRequest) -> HttpResponse:
    """A request handler which returns some text"""
    return HttpResponse(
        200,
        [(b'content-type', b'text/plain')],
        text_writer('This is not a test')
    )


if __name__ == "__main__":
    app = Application()
    app.http_router.add({'GET'}, '/{rest:path}', http_request_callback)

    uvicorn.run(app, port=9009)

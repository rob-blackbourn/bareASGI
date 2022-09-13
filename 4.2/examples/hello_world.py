"""Hello, World!"""

import uvicorn

from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    text_writer
)

app = Application()


@app.on_http_request({'GET'}, '/')
async def http_request_callback(_request: HttpRequest) -> HttpResponse:
    """A request handler which returns some text"""
    return HttpResponse(
        200,
        [(b'content-type', b'text/plain')],
        text_writer('Hello, World!')
    )

uvicorn.run(app, port=9009)

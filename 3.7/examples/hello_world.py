"""Hello, World!"""

import uvicorn

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    text_writer
)

app = Application()


@app.on_http_request({'GET'}, '/')
async def http_request_callback(
        _scope: Scope,
        _info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    """A request handler which returns some text"""
    return 200, [(b'content-type', b'text/plain')], text_writer('Hello, World!')

uvicorn.run(app, port=9009)

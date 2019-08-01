"""
A simple web page example
"""
import asyncio
import logging
import os
import socket
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

logger = logging.getLogger('server_sent_events')


# pylint: disable=unused-argument
async def index(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """Redirect to the example"""
    return 303, [(b'Location', b'/example1')]


# pylint: disable=unused-argument
async def test_page1(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A request handler which returns some html"""
    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Example 1</title>
  </head>
  <body>
    <h1>Example 1</h1>
    
    <p>This is simple<p>
  </body>
</html>

"""
    return 200, [(b'content-type', b'text/html')], text_writer(html)


# pylint: disable=unused-argument
async def test_page2(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A request handler which returns HTML"""
    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Example 2</title>
  </head>
  <body>
    <h1>Example 2</h1>

    <p>This is simple<p>
  </body>
</html>
"""
    return 200, [(b'content-type', b'text/html')], text_writer(html)


# pylint: disable=unused-argument
async def test_empty(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A request handler which only returns a valid "no content" status"""
    return 204


if __name__ == "__main__":
    app = Application()

    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/example1', test_page1)
    app.http_router.add({'GET'}, '/example2', test_page2)
    app.http_router.add({'GET'}, '/empty', test_empty)

    import uvicorn
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    USE_UVICORN = False
    host = socket.gethostname()

    if USE_UVICORN:
        uvicorn.run(app, port=9009)
    else:
        config = Config()
        config.bind = ["127.0.0.1:9009"]
        config.certfile = os.path.expanduser(f"~/.keys/{host}.crt")
        config.keyfile = os.path.expanduser(f"~/.keys/{host}.key")
        asyncio.run(serve(app, config))

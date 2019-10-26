"""
An example of HTTP/2 server push.
"""

import asyncio
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

logger = logging.getLogger('server_sent_events')


# pylint: disable=unused-argument
async def index(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A request handler which redirects to an index file"""
    return 303, [(b'Location', b'/index.html')]


# pylint: disable=unused-argument
async def test_page(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A request handler which returns an HTML document with secondary content"""

    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Example 1</title>
    <script src="/clickHandler.js"></script>
  </head>
  <body>
    <h1>Example 1</h1>
    <button type="button" onclick="handleClick('here')">
        Click me
    </button>
    <p id="here" />
    <script
  </body>
</html>

"""
    pushes = [
        ('/clickhandler.js', [(b'accept', b'text/javascript')])
    ]
    return 200, [(b'content-type', b'text/html')], text_writer(html), pushes


# pylint: disable=unused-argument
async def test_asset(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A request handler which provides an asset required by the html."""
    js_content = """
function handleClick(id) {
  document.getElementById(id).innerHTML = Date()
}
"""
    return 200, [(b'content-type', b'text/javascript')], text_writer(js_content)


if __name__ == "__main__":
    app = Application()

    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/index.html', test_page)
    app.http_router.add({'GET'}, '/clickHandler.js', test_asset)

    import uvicorn
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    USE_UVICORN = False

    if USE_UVICORN:
        uvicorn.run(app, port=9009)
    else:
        config = Config()
        config.bind = ["ugsb-rbla01.bhdgsystematic.com:9009"]
        config.certfile = "/home/BHDGSYSTEMATIC.COM/rblackbourn/.keys/ugsb-rbla01.crt"
        config.keyfile = "/home/BHDGSYSTEMATIC.COM/rblackbourn/.keys/ugsb-rbla01.key"
        asyncio.run(serve(app, config))

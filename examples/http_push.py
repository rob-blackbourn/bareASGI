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

log = logging.getLogger('server_sent_events')


# noinspection PyUnusedLocal
async def index(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    return 303, [(b'Location', b'/index.html')], None, None


# noinspection PyUnusedLocal
async def test_page(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
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


# noinspection PyUnusedLocal
async def test_asset(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    js = """
function handleClick(id) {
  document.getElementById(id).innerHTML = Date()
}
"""
    return 200, [(b'content-type', b'text/javascript')], text_writer(js)


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

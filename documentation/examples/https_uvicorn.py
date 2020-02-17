"""
A simple web page example
"""
import logging
import os.path

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

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger('server_sent_events')


async def test_page(
        _scope: Scope,
        _info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    """A request handler which returns some html"""
    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Uvicorn http</title>
  </head>
  <body>
    <h1>Uvicorn https</h1>
    
    <p>I'm secure<p>
  </body>
</html>
"""
    return 200, [(b'content-type', b'text/html')], text_writer(html)


if __name__ == "__main__":
    app = Application()

    app.http_router.add({'GET'}, '/', test_page)

    uvicorn.run(
        app,
        host='0.0.0.0',
        port=9009,
        ssl_certfile=os.path.expanduser(f"~/.keys/server.crt"),
        ssl_keyfile=os.path.expanduser(f"~/.keys/server.key")
    )

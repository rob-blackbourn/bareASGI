"""Using HTTPS with hypercorn"""

import asyncio
import logging
import os.path
import signal
from typing import Any

from hypercorn.asyncio import serve
from hypercorn.config import Config

from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger('server_sent_events')


async def test_page(_request: HttpRequest) -> HttpResponse:
    """A request handler which returns some html"""
    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Hypercorn http</title>
  </head>
  <body>
    <h1>Hypercorn https</h1>
    
    <p>I'm secure<p>
  </body>
</html>
"""
    return HttpResponse(
        200,
        [(b'content-type', b'text/html')],
        text_writer(html)
    )

if __name__ == "__main__":
    app = Application()

    app.http_router.add({'GET'}, '/', test_page)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    shutdown_event = asyncio.Event()

    def _signal_handler(*_: Any) -> None:
        shutdown_event.set()
    loop.add_signal_handler(signal.SIGTERM, _signal_handler)
    loop.add_signal_handler(signal.SIGINT, _signal_handler)

    config = Config()
    config.bind = ["0.0.0.0:9009"]
    config.loglevel = 'debug'
    config.certfile = os.path.expanduser("~/.keys/server.crt")
    config.keyfile = os.path.expanduser("~/.keys/server.key")

    loop.run_until_complete(
        serve(
            app, # type: ignore
            config,
            shutdown_trigger=shutdown_event.wait  # type: ignore
        )
    )

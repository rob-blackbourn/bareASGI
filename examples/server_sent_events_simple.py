"""
A simple example of server sent events.
"""

import asyncio
from datetime import datetime
import logging
from typing import Any

from bareasgi import (
    Application,
    text_writer,
    HttpRequest,
    HttpResponse,
    LifespanRequest
)

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)


async def on_startup(_request: LifespanRequest) -> None:
    """Run at startup"""
    LOGGER.info("Running startup handler")


async def on_shutdown(_request: LifespanRequest) -> None:
    """Run on shutdown"""
    LOGGER.info("Running shutdown handler")


async def index(_request: HttpRequest) -> HttpResponse:
    """Redirect to the index page"""
    return HttpResponse(303, [(b'Location', b'/test')], None)


async def test_page(_request: HttpRequest) -> HttpResponse:
    """A request handler which provides the page to respond to server sent events"""
    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Example</title>
  </head>
  <body>
    <h1>Server Sent Events</h1>
    
    Time: <snap id="time"></span>
    
    <script>
      var eventSource = new EventSource("/events")
      eventSource.onmessage = function(event) {
        element = document.getElementById("time")
        element.innerHTML = event.data
      }
    </script>
  </body>
</html>

"""
    return HttpResponse(
        200,
        [(b'content-type', b'text/html')],
        text_writer(html)
    )


async def test_events(_request: HttpRequest) -> HttpResponse:
    """A request handler which provides server sent events"""

    async def send_events():
        is_cancelled = False
        while not is_cancelled:
            try:
                LOGGER.debug('Sending event')
                yield f'data: {datetime.now()}\n\n\n'.encode('utf-8')
                # Defeat buffering by giving the server a nudge.
                yield ':\n\n\n'.encode('utf-8')
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                LOGGER.debug('Cancelled')
                is_cancelled = True
            except:  # pylint: disable=bare-except
                LOGGER.exception('Failed')

    headers = [
        (b'cache-control', b'no-cache'),
        (b'content-type', b'text/event-stream'),
        (b'connection', b'keep-alive')
    ]

    return HttpResponse(200, headers, send_events())


if __name__ == "__main__":
    app = Application(
        startup_handlers=[on_startup],
        shutdown_handlers=[on_shutdown]
    )

    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/test', test_page)
    app.http_router.add({'GET'}, '/events', test_events)

    USE_UVICORN = True

    if USE_UVICORN:
        import uvicorn
        uvicorn.run(app, port=9009)
    else:
        import signal
        import uvloop
        from hypercorn.asyncio import serve
        from hypercorn.config import Config
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        shutdown_event = asyncio.Event()

        def _signal_handler(*_: Any) -> None:
            shutdown_event.set()
        loop.add_signal_handler(signal.SIGTERM, _signal_handler)
        loop.add_signal_handler(signal.SIGINT, _signal_handler)

        config = Config()
        config.bind = ["0.0.0.0:9009"]
        loop.run_until_complete(
            serve(
                app,  # type: ignore
                config,
                shutdown_trigger=shutdown_event.wait  # type: ignore
            )
        )

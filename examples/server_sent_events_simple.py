"""
A simple example of server sent events.
"""

import asyncio
from datetime import datetime
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
async def index(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    """Redirect to the index page"""
    return 303, [(b'Location', b'/test')], None


# pylint: disable=unused-argument
async def test_page(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
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
      var eventSource = new EventSource("http://localhost:9009/events")
      eventSource.onmessage = function(event) {
        element = document.getElementById("time")
        element.innerHTML = event.data
      }
    </script>
  </body>
</html>

"""
    return 200, [(b'content-type', b'text/html')], text_writer(html)


# pylint: disable=unused-argument
async def test_events(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A request handler which provides server sent events"""

    async def send_events():
        is_cancelled = False
        while not is_cancelled:
            try:
                logger.debug('Sending event')
                yield f'data: {datetime.now()}\n\n\n'.encode('utf-8')
                # Defeat buffering by giving the server a nudge.
                yield ':\n\n\n'.encode('utf-8')
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                logger.debug('Cancelled')
                is_cancelled = True

    headers = [
        (b'cache-control', b'no-cache'),
        (b'content-type', b'text/event-stream'),
        (b'connection', b'keep-alive')
    ]

    return 200, headers, send_events()


if __name__ == "__main__":
    import uvicorn

    app = Application()

    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/test', test_page)
    app.http_router.add({'GET'}, '/events', test_events)

    uvicorn.run(app, host='localhost', port=9009)

"""
A more useful exammple of server sent events.

Here listeners are provided with queues with which they monitor
the event source. This means the event source can support many
listeners.
"""

import asyncio
from asyncio import Event
from asyncio.queues import Queue
from datetime import datetime
import logging
from typing import AsyncGenerator

from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    LifespanRequest,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger('server_sent_events')


class TimeTicker:
    """An event source which supports queue based notification"""

    def __init__(self) -> None:
        self.shutdown_event = Event()
        self.listeners: list[Queue] = []

    async def start(self) -> None:
        """Start generating events"""

        while not self.shutdown_event.is_set():
            now = datetime.now()
            for listener in self.listeners:
                await listener.put(now)
            try:
                await asyncio.wait_for(self.shutdown_event.wait(), timeout=1)
            except asyncio.TimeoutError:
                pass
            except:  # pylint: disable=bare-except
                LOGGER.exception('Cancelled')

    def stop(self):
        """Stop the event source"""
        self.shutdown_event.set()

    def add_listener(self) -> Queue:
        """Add a listener to the event source"""
        LOGGER.debug('Adding a listener')
        listener: Queue = Queue()
        self.listeners.append(listener)
        return listener

    def remove_listener(self, listener: Queue) -> None:
        """Remove a listener from the event source"""
        self.listeners.remove(listener)


async def start_time_ticker(request: LifespanRequest) -> None:
    """A startup task that starts the time ticker.

    It is important that the task gets created by the startup task as the
    asyncio objects created (Event and Queue) must be create with the event
    loop of the ASGI server.
    """
    time_ticker = TimeTicker()
    request.info['time_ticker'] = time_ticker
    request.info['time_ticker_task'] = asyncio.create_task(time_ticker.start())


async def stop_time_ticker(request: LifespanRequest) -> None:
    """Stop the time ticker"""
    time_ticker: TimeTicker = request.info['time_ticker']
    LOGGER.debug('Stopping time_ticker')
    time_ticker.stop()
    time_ticker_task: asyncio.Task = request.info['time_ticker_task']
    LOGGER.debug('Waiting for time_ticker')
    await time_ticker_task
    LOGGER.debug('time_ticker shutdown')


async def index(_request: HttpRequest) -> HttpResponse:
    """Redirect to the test page"""
    return HttpResponse(303, [(b'Location', b'/test')])


async def test_page(_request: HttpRequest) -> HttpResponse:
    """A simple page which receives server sent events"""
    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Server Sent Evets</title>
  </head>
  <body>
    <h1>Server Sent Events</h1>
    
    Time: <snap id="time"></span>
    
    <script>
      var eventSource = new EventSource("http://localhost:9009/events")
      eventSource.onmessage = function(event) {
        console.log('onmessage', event)
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


async def test_event(request: HttpRequest) -> HttpResponse:
    """This request handler provides the server sent events."""

    # Get the time ticker event source from the application's info parameter.
    time_ticker: TimeTicker = request.info['time_ticker']
    listener = time_ticker.add_listener()

    async def listen() -> AsyncGenerator[bytes, None]:
        is_cancelled = False
        while not is_cancelled:
            try:
                now: datetime = await listener.get()
                yield f'data: {now}\n\n\n'.encode('utf-8')
                # Defeat buffering by giving the server a nudge.
                yield ':\n\n\n'.encode('utf-8')
            except asyncio.CancelledError:
                is_cancelled = True
        LOGGER.debug('Done')

    headers = [
        (b'cache-control', b'no-cache'),
        (b'content-type', b'text/event-stream'),
        (b'transfer-encoding', b'chunked')
    ]
    return HttpResponse(200, headers, listen())


if __name__ == "__main__":
    import uvicorn

    app = Application(
        info=dict(),
        startup_handlers=[start_time_ticker],
        shutdown_handlers=[stop_time_ticker]
    )

    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/test', test_page)
    app.http_router.add({'GET'}, '/events', test_event)

    uvicorn.run(app, host='localhost', port=9009)

import asyncio
from asyncio import Event
from asyncio.queues import Queue
from datetime import datetime
import logging
from typing import List
from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    Message,
    HttpResponse,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger('server_sent_events')


class TimeTicker:

    def __init__(self) -> None:
        self.shutdown_event = Event()
        self.listeners: List[Queue] = []

    async def start(self) -> None:
        while not self.shutdown_event.is_set():
            now = datetime.now()
            for listener in self.listeners:
                await listener.put(now)
            try:
                await asyncio.wait_for(self.shutdown_event.wait(), timeout=1)
            except asyncio.TimeoutError:
                pass
            except:
                log.exception('Cancelled')

    def stop(self):
        self.shutdown_event.set()

    def add_listener(self) -> Queue:
        log.debug('Adding a listener')
        listener = Queue()
        self.listeners.append(listener)
        return listener

    def remove_listener(self, listener: Queue) -> None:
        self.listeners.remove(listener)


# noinspection PyUnusedLocal
async def start_time_ticker(scope: Scope, info: Info, request: Message) -> None:
    time_ticker = TimeTicker()
    info['time_ticker'] = time_ticker
    info['time_ticker_task'] = asyncio.create_task(time_ticker.start())


# noinspection PyUnusedLocal
async def stop_time_ticker(scope: Scope, info: Info, request: Message) -> None:
    time_ticker: TimeTicker = info['time_ticker']
    log.debug('Stopping time_ticker')
    time_ticker.stop()
    time_ticker_task: asyncio.Task = info['time_ticker_task']
    log.debug('Waiting for time_ticker')
    await time_ticker_task
    log.debug('time_ticker shutdown')


# noinspection PyUnusedLocal
async def index(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    return 303, [(b'Location', b'/test')], None


# noinspection PyUnusedLocal
async def test_page(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
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

    return 200, [(b'content-type', b'text/html')], text_writer(html)


# noinspection PyUnusedLocal
async def test_event(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    time_ticker: TimeTicker = info['time_ticker']
    listener = time_ticker.add_listener()

    async def listen():
        is_cancelled = False
        while not is_cancelled:
            try:
                now: datetime = await listener.get()
                yield f'data: {now}\n\n\n'.encode('utf-8')
            except asyncio.CancelledError:
                is_cancelled = True
        log.debug('Done')

    headers = [
        (b'cache-control', b'no-cache'),
        (b'content-type', b'text/event-stream'),
        (b'transfer-encoding', b'chunked')
    ]
    return 200, headers, listen()


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

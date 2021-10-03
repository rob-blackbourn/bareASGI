"""
A simple example of server sent events.
"""

import asyncio
from datetime import datetime
import json
import logging
import signal
import string
from typing import Any

from hypercorn.asyncio import serve
from hypercorn.config import Config
import pkg_resources

from bareasgi import (
    Application,
    HttpResponse,
    text_reader,
    text_writer
)
import bareutils.header as header

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('server_sent_events')


async def index(_request):
    """Redirect to the index page"""
    return HttpResponse(303, [(b'Location', b'/test')])


async def test_page(request):
    """A request handler which provides the page to respond to server sent events"""
    host = header.find_exact(b'host', request.scope['headers']).decode()
    fetch_url = f"{request.scope['scheme']}://{host}/events"
    html = request.info['page_template'].substitute(__FETCH_URL__=fetch_url)
    return HttpResponse(200, [(b'content-type', b'text/html')], text_writer(html))


async def test_events(request):
    """A request handler which provides server sent events"""

    body = await text_reader(request.body)
    data = json.loads(body)

    async def send_events():
        is_cancelled = False
        while not is_cancelled:
            try:
                logger.debug('Sending event')
                message = {
                    'type': 'tick',
                    'data': {
                        'time': datetime.now().isoformat(),
                        'message': data['message']
                    }
                }
                line = json.dumps(message) + '\n'
                yield line.encode('utf-8')
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                logger.debug('Cancelled')
                is_cancelled = True

    headers = [
        (b'cache-control', b'no-cache'),
        (b'content-type', b'application/json'),
        (b'connection', b'keep-alive')
    ]

    return HttpResponse(200, headers, send_events())


if __name__ == "__main__":

    page_filename = pkg_resources.resource_filename(
        __name__,
        "streaming_fetch.html"
    )
    with open(page_filename, 'rt', encoding='utf-8') as file_ptr:
        page = file_ptr.read()

    app = Application(info={'page_template': string.Template(page)})

    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/test', test_page)
    app.http_router.add({'POST', 'OPTION'}, '/events', test_events)

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

    loop.run_until_complete(
        serve(
            app,  # type: ignore
            config,
            shutdown_trigger=shutdown_event.wait  # type: ignore
        )
    )

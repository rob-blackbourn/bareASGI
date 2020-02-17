import asyncio
from datetime import datetime

from bareasgi import Application, text_writer
import pkg_resources
import uvicorn


async def index(scope, info, matches, content):
    return 303, [(b'Location', b'/test')], None

async def test_page(scope, info, matches, content):
    return 200, [(b'content-type', b'text/html')], text_writer(info['html'])

async def test_events(scope, info, matches, content):

    async def send_events():
        is_cancelled = False
        while not is_cancelled:
            try:
                print('Sending event')
                yield f'data: {datetime.now()}\n\n\n'.encode('utf-8')
                # Defeat buffering by giving the server a nudge.
                yield ':\n\n\n'.encode('utf-8')
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                print('Cancelled')
                is_cancelled = True
            except:  # pylint: disable=bare-except
                print('Failed')

    headers = [
        (b'cache-control', b'no-cache'),
        (b'content-type', b'text/event-stream'),
        (b'connection', b'keep-alive')
    ]

    return 200, headers, send_events()


html_filename = pkg_resources.resource_filename(
    __name__,
    "server_sent_events.html"
)
with open(html_filename, 'rt') as file_ptr:
    html = file_ptr.read()

app = Application(info=dict(html=html))

app.http_router.add({'GET'}, '/', index)
app.http_router.add({'GET'}, '/test', test_page)
app.http_router.add({'GET'}, '/events', test_events)

uvicorn.run(app, port=9009)

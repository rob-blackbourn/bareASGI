# Exceptions

The bareASGI framework handles the exception of type `urllib.error.HTTPError`.

The source code for the following example can be found
[here](../examples/exceptions_nt.py)
(and here [here](../examples/exceptions.py) with typing).

If the content of the exception is specified it may be either an asynchronous
iterator yielding bytes, a string or a bytes.

Here are some examples.

```python
from urllib.error import HTTPError

from bareasgi import Application, text_writer
import bareutils.header as header
import pkg_resources
import uvicorn

def make_url(scope) -> str:
    host = header.find(b'host', scope['headers'], b'unknown').decode()
    return f"{scope['scheme']}://{host}{scope['path']}"

async def index_handler(scope, info, matches, content):
    headers = [
        (b'content-type', b'text/html')
    ]
    return 200, headers, text_writer(info['html'])


async def raise_none_exception(scope, info, matches, content):
    raise HTTPError(
        make_url(scope),
        401,
        None,
        None,
        None
    )

async def raise_text_exception(scope, info, matches, content):
    raise HTTPError(
        make_url(scope),
        401,
        'Unauthorized - text',
        [(b'content-type', b'text/plain')],
        None
    )

async def raise_bytes_exception(scope, info, matches, content):
    raise HTTPError(
        make_url(scope),
        401,
        b'Unauthorized - bytes',
        [(b'content-type', b'text/plain')],
        None
    )


async def raise_writer_exception(scope, info, matches, content):
    raise HTTPError(
        make_url(scope),
        401,
        text_writer('Unauthorized - writer'),
        [(b'content-type', b'text/plain')],
        None
    )

html_filename = pkg_resources.resource_filename(__name__, "server_sent_events.html")
with open(html_filename, 'rt') as file_ptr:
    html = file_ptr.read()

app = Application(info=dict(html=html))
app.http_router.add({'GET'}, '/', index_handler)
app.http_router.add({'GET'}, '/raise_none_exception',raise_none_exception)
app.http_router.add({'GET'}, '/raise_text_exception', raise_text_exception)
app.http_router.add({'GET'}, '/raise_bytes_exception', raise_bytes_exception)
app.http_router.add({'GET'}, '/raise_writer_exception', raise_writer_exception)

uvicorn.run(app, port=9009)

```

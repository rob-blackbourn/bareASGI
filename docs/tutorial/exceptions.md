# Exceptions

The bareASGI framework handles the exception of type `bareasgi.HttpError`.

The source code for the following example can be found
[here](../examples/exceptions_nt.py)
(and here [here](../examples/exceptions.py) with typing).

If the content of the exception is specified it may be either an asynchronous
iterator yielding bytes, a string or a bytes.

Here are some examples.

```python
from bareasgi import Application, text_writer, HttpError
import bareutils.header as header
import pkg_resources
import uvicorn

async def index_handler(request):
    headers = [
        (b'content-type', b'text/html')
    ]
    return 200, headers, text_writer(info['html'])


async def raise_none_exception(request):
    raise HttpError(
        401,
        url=request.url
    )

async def raise_text_exception(request):
    raise HttpError(
        401,
        'Unauthorized - text',
        url=request.url,
        [(b'content-type', b'text/plain')],
    )

async def raise_bytes_exception(request):
    raise HttpError(
        401,
        url=request.url,
        b'Unauthorized - bytes',
        [(b'content-type', b'text/plain')],
        None
    )


async def raise_writer_exception(request):
    raise HttpError(
        401,
        text_writer('Unauthorized - writer'),
        url=request.url,
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

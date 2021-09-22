from bareasgi import Application, text_writer, HttpError, HttpRequest, HttpResponse
from bareutils import header
import pkg_resources
import uvicorn


def make_url(scope) -> str:
    host = header.find(b'host', scope['headers'], b'unknown').decode()
    return f"{scope['scheme']}://{host}{scope['path']}"


async def index_handler(request):
    headers = [
        (b'content-type', b'text/html')
    ]
    return 200, headers, text_writer(request.info['html'])


async def raise_none_exception(request):
    raise HttpError(
        401,
        url=make_url(request.scope),
    )


async def raise_text_exception(request):
    raise HttpError(
        401,
        'Unauthorized - text',
        make_url(request.scope),
        [(b'content-type', b'text/plain')],
    )


async def raise_writer_exception(scope, info, matches, content):
    raise HttpError(
        401,
        make_url(scope),
        text_writer('Unauthorized - writer'),
        [(b'content-type', b'text/plain')],
        None
    )

html_filename = pkg_resources.resource_filename(
    __name__, "server_sent_events.html")
with open(html_filename, 'rt') as file_ptr:
    html = file_ptr.read()

app = Application(info=dict(html=html))
app.http_router.add({'GET'}, '/', index_handler)
app.http_router.add({'GET'}, '/raise_none_exception', raise_none_exception)
app.http_router.add({'GET'}, '/raise_text_exception', raise_text_exception)
app.http_router.add({'GET'}, '/raise_writer_exception', raise_writer_exception)

uvicorn.run(app, port=9009)

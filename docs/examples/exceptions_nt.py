import pkg_resources
import uvicorn

from bareasgi import Application, text_writer, HttpError, HttpResponse


async def index_handler(request):
    return HttpResponse(
        200,
        [(b'content-type', b'text/html')],
        text_writer(request.info['html'])
    )


async def raise_none_exception(request):
    raise HttpError(401)


async def raise_text_exception(request):
    raise HttpError(
        401,
        [(b'content-type', b'text/plain')],
        'Unauthorized - text',
    )


async def raise_writer_exception(request):
    raise HttpError(
        401,
        [(b'content-type', b'text/plain')],
        text_writer('Unauthorized - writer'),
    )

html_filename = pkg_resources.resource_filename(
    __name__,
    "server_sent_events.html"
)

with open(html_filename, 'rt', encoding='utf-8') as file_ptr:
    html = file_ptr.read()

app = Application(info=dict(html=html))
app.http_router.add({'GET'}, '/', index_handler)
app.http_router.add({'GET'}, '/raise_none_exception', raise_none_exception)
app.http_router.add({'GET'}, '/raise_text_exception', raise_text_exception)
app.http_router.add({'GET'}, '/raise_writer_exception', raise_writer_exception)

uvicorn.run(app, port=9009)

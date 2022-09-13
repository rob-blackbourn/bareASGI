import uvicorn
from bareasgi import Application, HttpResponse, bytes_writer
from bareasgi.middlewares import make_default_compression_middleware


async def http_request_callback(_request):
    with open(__file__, 'rb') as file_pointer:
        buf = file_pointer.read()

    headers = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(len(buf)).encode('ascii'))
    ]

    return HttpResponse(200, headers, bytes_writer(buf, chunk_size=-1))

compression_middleware = make_default_compression_middleware(minimum_size=1024)

app = Application(middlewares=[compression_middleware])

app.http_router.add({'GET'}, '/{rest:path}', http_request_callback)

uvicorn.run(app, port=9009)

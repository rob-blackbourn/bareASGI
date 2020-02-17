from bareutils.compression import make_default_compression_middleware
from bareasgi import Application, bytes_writer
import uvicorn

async def http_request_callback(scope, info, matches, content):
    with open(__file__, 'rb') as file_pointer:
        buf = file_pointer.read()

    headers = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(len(buf)).encode('ascii'))
    ]

    return 200, headers, bytes_writer(buf, chunk_size=-1)

compression_middleware = make_default_compression_middleware(minimum_size=1024)

app = Application(middlewares=[compression_middleware])

app.http_router.add({'GET'}, '/{rest:path}', http_request_callback)

uvicorn.run(app, port=9009)

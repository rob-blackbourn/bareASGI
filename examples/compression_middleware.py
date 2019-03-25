import logging
from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    bytes_writer
)
from bareasgi.compression.middleware import make_default_compression_middleware

logging.basicConfig(level=logging.DEBUG)


async def http_request_callback(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    with open(__file__, 'rb') as fp:
        buf = fp.read()

    headers = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(len(buf)).encode('ascii'))
    ]

    return 200, headers, bytes_writer(buf, chunk_size=-1)


if __name__ == "__main__":
    import uvicorn

    compression_middleware = make_default_compression_middleware(minimum_size=1024)

    app = Application(middlewares=[compression_middleware])

    app.http_router.add({'GET'}, '/{rest:path}', http_request_callback)

    uvicorn.run(app, port=9009)

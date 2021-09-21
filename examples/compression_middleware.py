"""
An example of using compression middleware for automatic compression
"""

import logging

from bareutils.compression import make_default_compression_middleware
from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    bytes_writer
)

logging.basicConfig(level=logging.DEBUG)


async def http_request_callback(_request: HttpRequest) -> HttpResponse:
    """A response handler which returns some text"""
    with open(__file__, 'rb') as file_pointer:
        buf = file_pointer.read()

    headers = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(len(buf)).encode('ascii'))
    ]

    return HttpResponse(200, headers, bytes_writer(buf, chunk_size=-1))


if __name__ == "__main__":
    import uvicorn

    # pylint: disable=invalid-name
    compression_middleware = make_default_compression_middleware(
        minimum_size=1024)

    app = Application(middlewares=[compression_middleware])

    app.http_router.add({'GET'}, '/{rest:path}', http_request_callback)

    uvicorn.run(app, port=9009)

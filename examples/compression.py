"""
Compression examples
"""

import logging

from bareutils import (
    compression_writer,
    make_compress_compressobj,
    make_deflate_compressobj,
    make_gzip_compressobj
)
from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)


async def gzip_compression(_request: HttpRequest) -> HttpResponse:
    """A request handler that returns it's content compressed with gzip"""
    with open(__file__, 'rb') as file_pointer:
        buf = file_pointer.read()
    headers = [
        (b'content-type', b'text/plain'),
        (b'content-encoding', b'gzip')
    ]

    return HttpResponse(
        200,
        headers,
        compression_writer(buf, make_gzip_compressobj(), 512)
    )


async def deflate_compression(_request: HttpRequest) -> HttpResponse:
    """A request handler which compresses it's content using the deflate method"""
    with open(__file__, 'rb') as file_pointer:
        buf = file_pointer.read()
    headers = [
        (b'content-type', b'text/plain'),
        (b'content-encoding', b'deflate')
    ]

    return HttpResponse(
        200,
        headers,
        compression_writer(buf, make_deflate_compressobj(), 512)
    )


async def compress_compression(_request: HttpRequest) -> HttpResponse:
    """A request handler which compresses it's content using the compress method"""
    with open(__file__, 'rb') as file_pointer:
        buf = file_pointer.read()
    headers = [
        (b'content-type', b'text/plain'),
        (b'content-encoding', b'compress')
    ]

    return HttpResponse(
        200,
        headers,
        compression_writer(buf, make_compress_compressobj(), 512)
    )


async def index(_request: HttpRequest) -> HttpResponse:
    """A request handler which provides an index of the compression methods"""
    html = """
<!DOCTYPE html>
<html>
  <body>
    <ul>
      <li><a href='/gzip'>gzip</a></li>
      <li><a href='/deflate'>deflate</a></li>
      <li><a href='/compress'>compress</a></li>
    </ul>
  </body>
</html>
"""
    return HttpResponse(
        200,
        [(b'content-type', b'text/html')],
        text_writer(html)
    )


if __name__ == "__main__":
    import uvicorn

    app = Application()
    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/gzip', gzip_compression)
    app.http_router.add({'GET'}, '/deflate', deflate_compression)
    app.http_router.add({'GET'}, '/compress', compress_compression)

    uvicorn.run(app, port=9009)

import logging
from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    text_writer
)

from bareasgi.compression import (
    compression_writer,
    make_compress_compressobj,
    make_deflate_compressobj,
    make_gzip_compressobj
)

logging.basicConfig(level=logging.DEBUG)


async def gzip_compression(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    with open(__file__, 'rb') as fp:
        buf = fp.read()
    headers = [
        (b'content-type', b'text/plain'),
        (b'content-encoding', b'gzip')
    ]

    return 200, headers, compression_writer(buf, make_gzip_compressobj(), 512)


async def deflate_compression(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    with open(__file__, 'rb') as fp:
        buf = fp.read()
    headers = [
        (b'content-type', b'text/plain'),
        (b'content-encoding', b'deflate')
    ]

    return 200, headers, compression_writer(buf, make_deflate_compressobj(), 512)


async def compress_compression(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:

    with open(__file__, 'rb') as fp:
        buf = fp.read()
    headers = [
        (b'content-type', b'text/plain'),
        (b'content-encoding', b'compress')
    ]

    return 200, headers, compression_writer(buf, make_compress_compressobj(), 512)


async def index(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
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
    return 200, [(b'content-type', b'text/html')], text_writer(html)


if __name__ == "__main__":
    import uvicorn

    app = Application()
    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/gzip', gzip_compression)
    app.http_router.add({'GET'}, '/deflate', deflate_compression)
    app.http_router.add({'GET'}, '/compress', compress_compression)

    uvicorn.run(app, port=9009)

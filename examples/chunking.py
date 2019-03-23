"""
Looking at different methods of transferring data.

ASGI will automatically chunk if the data is sent in more than one packet or
if the content length is omitted.

A browser will show 'transfer-encoding' as 'chunked' for all cases except 'with content length'
"""

import logging
from typing import AsyncGenerator
from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse
)

logging.basicConfig(level=logging.DEBUG)

async def non_chunking_writer(text: str, encoding: str = 'utf-8') -> AsyncGenerator[bytes, None]:
    yield text.encode(encoding=encoding)

async def chunking_writer(text: str, encoding: str = 'utf-8', bufsiz:int=512) -> AsyncGenerator[bytes, None]:
    start, end = 0, bufsiz
    while start < len(text):
        yield text[start:end].encode(encoding=encoding)
        start, end = end, end + bufsiz


async def with_chunking(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    return 200, [(b'content-type', b'text/plain')], chunking_writer(info['text'], bufsiz=64)

async def without_chunking(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    return 200, [(b'content-type', b'text/plain')], non_chunking_writer(info['text'])

async def with_content_length(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    headers = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(len(info['text'])).encode('ascii')),
    ]
    return 200, headers, non_chunking_writer(info['text'])

async def with_content_length_and_chunking(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    headers = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(len(info['text'])).encode('ascii')),
    ]
    return 200, headers, chunking_writer(info['text'])

async def invalid_content_length_and_chunking(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    headers = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(int(len(info['text'])/2)).encode('ascii')),
    ]
    return 200, headers, chunking_writer(info['text'])

async def index(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    html = """
<!DOCTYPE html>
<html>
  <body>
    <ul>
      <li><a href='/with_chunking'>with chunking</a></li>
      <li><a href='/without_chunking'>without chunking</a></li>
      <li><a href='/with_content_length'>with content_length</a></li>
      <li><a href='/with_content_length_and_chunking'>with content_length and chunking</a></li>
      <li><a href='/invalid_content_length_and_chunking'>invalid content_length and chunking</a></li>
    </ul>
  </body>
</html>
"""
    return 200, [(b'content-type', b'text/html')], non_chunking_writer(html)



if __name__ == "__main__":
    import uvicorn

    # Use this file as the data to send.
    with open(__file__, 'rt') as fp:
        text = fp.read()

    app = Application(info={'text': text})

    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/with_chunking', with_chunking)
    app.http_router.add({'GET'}, '/without_chunking', without_chunking)
    app.http_router.add({'GET'}, '/with_content_length', with_content_length)
    app.http_router.add({'GET'}, '/with_content_length_and_chunking', with_content_length_and_chunking)
    app.http_router.add({'GET'}, '/invalid_content_length_and_chunking', invalid_content_length_and_chunking)

    uvicorn.run(app, port=9009)

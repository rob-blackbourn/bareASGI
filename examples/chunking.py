"""
Looking at different methods of transferring content.

The http response header "transfer-encoding" is automagically set by the ASGI
server to "chunked" if a "content-length" header is not specified.

Inn bareASGI the content is provided by an asynchronous generator. This allows
for efficient transfer of data in pieces, rather than as a single blob.

A browser will show 'transfer-encoding' as 'chunked' for all cases except 'with content length'

Usage
-----

Start the server and open the "Developer Tools" in the browser.
Looking at the "Network" click on each of the links and note
the "transfer-encoding" in the "Response Headers".
"""

import logging

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse
)

logging.basicConfig(level=logging.DEBUG)


async def non_chunking_writer(text: str, encoding: str = 'utf-8') -> Content:
    """A writer which yields the entire buffer"""
    yield text.encode(encoding=encoding)


async def chunking_writer(text: str, encoding: str = 'utf-8', bufsiz: int = 512) -> Content:
    """A writer which yields the buffer in multiple chunks"""
    start, end = 0, bufsiz
    while start < len(text):
        yield text[start:end].encode(encoding=encoding)
        start, end = end, end + bufsiz


# pylint: disable=unused-argument
async def with_chunking(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A response handler which sends it's body in chunks"""
    return 200, [(b'content-type', b'text/plain')], chunking_writer(info['text'], bufsiz=64)


# pylint: disable=unused-argument
async def without_chunking(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A response handler which sends it's body as a single chunk without content length"""
    return 200, [(b'content-type', b'text/plain')], non_chunking_writer(info['text'])


# pylint: disable=unused-argument
async def with_content_length(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A response handler which sends it's body without chunking and with content length"""
    headers = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(len(info['text'])).encode('ascii')),
    ]
    return 200, headers, non_chunking_writer(info['text'])


# pylint: disable=unused-argument
async def with_content_length_and_chunking(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A response handler which sends it's body in chunks with a content length"""
    headers = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(len(info['text'])).encode('ascii')),
    ]
    return 200, headers, chunking_writer(info['text'])


# pylint: disable=unused-argument
async def invalid_content_length_and_chunking(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A response handler which sends it's body in chunks with an invalid content length"""
    headers = [
        (b'content-type', b'text/plain'),
        (b'content-length', str(int(len(info['text']) / 2)).encode('ascii')),
    ]
    return 200, headers, chunking_writer(info['text'])


# pylint: disable=unused-argument
async def index(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A content handler providing an index of the chunking methods"""
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
        file_text = fp.read()  # pylint: disable=invalid-name

    app = Application(info={'text': file_text})

    app.http_router.add(
        {'GET'},
        '/',
        index
    )
    app.http_router.add(
        {'GET'},
        '/with_chunking',
        with_chunking
    )
    app.http_router.add(
        {'GET'},
        '/without_chunking',
        without_chunking
    )
    app.http_router.add(
        {'GET'},
        '/with_content_length',
        with_content_length
    )
    app.http_router.add(
        {'GET'},
        '/with_content_length_and_chunking',
        with_content_length_and_chunking
    )
    app.http_router.add(
        {'GET'},
        '/invalid_content_length_and_chunking',
        invalid_content_length_and_chunking
    )

    uvicorn.run(app, port=9009)

"""
A simple request handler.
"""

import logging
from typing import List, Tuple

from bareasgi import (
    Application,
    HttpError,
    HttpRequest,
    HttpResponse,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)


async def index_handler(_request: HttpRequest) -> HttpResponse:
    """The index page"""
    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Raising Exceptions</title>
  </head>
  <body>
    <h1>Raising Exceptions</h1>
    
    <ul>
        <li><a href="/raise_none_exception">
            Raise a 401 exception with no content
        </li>
        <li><a href="/raise_text_exception">
            Raise a 401 exception with text content
        </li>
        <li><a href="/raise_bytes_exception">
            Raise a 401 exception with bytes content
        </li>
        <li><a href="/raise_writer_exception">
            Raise a 401 exception with a writer providing content
        </li>
    </ul>
  </body>
</html>
"""
    headers: List[Tuple[bytes, bytes]] = [
        (b'content-type', b'text/html')
    ]
    return HttpResponse(200, headers, text_writer(html))


async def raise_none_exception(request: HttpRequest) -> HttpResponse:
    """A request handler which raises an exception no content"""
    raise HttpError(
        401,
        url=request.url
    )


async def raise_text_exception(request: HttpRequest) -> HttpResponse:
    """A request handler which raises an exception with text content"""
    raise HttpError(
        401,
        'Unauthorized - text',
        request.url,
        [(b'content-type', b'text/plain')],
    )


async def raise_bytes_exception(request: HttpRequest) -> HttpResponse:
    """A request handler which raises an exception with bytes content"""
    raise HttpError(
        401,
        b'Unauthorized - bytes',
        request.url,
        [(b'content-type', b'text/plain')],
    )


async def raise_writer_exception(request: HttpRequest) -> HttpResponse:
    """A request handler which raises an exception with a writer content"""
    raise HttpError(
        401,
        text_writer('Unauthorized - writer'),
        request.url,
        [(b'content-type', b'text/plain')]
    )


if __name__ == "__main__":
    import uvicorn

    app = Application()
    app.http_router.add(
        {'GET'},
        '/',
        index_handler
    )
    app.http_router.add(
        {'GET'},
        '/raise_none_exception',
        raise_none_exception
    )
    app.http_router.add(
        {'GET'},
        '/raise_text_exception',
        raise_text_exception
    )
    app.http_router.add(
        {'GET'},
        '/raise_bytes_exception',
        raise_bytes_exception
    )
    app.http_router.add(
        {'GET'},
        '/raise_writer_exception',
        raise_writer_exception
    )

    uvicorn.run(app, port=9009)

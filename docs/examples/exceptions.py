"""
An example of raising exceptions
"""

import logging
from typing import List

import pkg_resources
import uvicorn


from bareasgi import (
    Application,
    HttpError,
    HttpRequest,
    HttpResponse,
    Headers,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)


async def index_handler(request: HttpRequest) -> HttpResponse:
    """The index page"""
    headers: List[Headers] = [
        (b'content-type', b'text/html')
    ]
    return HttpResponse(200, headers, text_writer(request.info['html']))


async def raise_none_exception(request: HttpRequest) -> HttpResponse:
    """A request handler which raises an exception no content"""
    raise HttpError(
        401,
        url=request.url,
    )


async def raise_text_exception(request: HttpRequest) -> HttpResponse:
    """A request handler which raises an exception with text content"""
    raise HttpError(
        401,
        'Unauthorized - text',
        request.url
        [(b'content-type', b'text/plain')]
    )


async def raise_bytes_exception(request: HttpRequest) -> HttpResponse:
    """A request handler which raises an exception with bytes content"""
    raise HttpError(
        401,
        b'Unauthorized - bytes',
        request.url,
        [(b'content-type', b'text/plain')]
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
    html_filename = pkg_resources.resource_filename(
        __name__, "exceptions.html")
    with open(html_filename, 'rt', encoding='utf-8') as file_ptr:
        html = file_ptr.read()

    app = Application(info=dict(html=html))
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

"""
An example of raising exceptions
"""

import logging
from typing import List
from urllib.error import HTTPError

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    Headers,
    text_writer
)
import bareutils.header as header
import pkg_resources
import uvicorn

logging.basicConfig(level=logging.DEBUG)


def make_url(scope: Scope) -> str:
    """Make the url from the scope"""
    host = header.find(b'host', scope['headers'], b'unknown').decode()
    return f"{scope['scheme']}://{host}{scope['path']}"


async def index_handler(
        _scope: Scope,
        info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    """The index page"""
    headers: List[Headers] = [
        (b'content-type', b'text/html')
    ]
    return 200, headers, text_writer(info['html'])


async def raise_none_exception(
        scope: Scope,
        _info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    """A request handler which raises an exception no content"""
    raise HTTPError(
        make_url(scope),
        401,
        None,
        None,
        None
    )
    # pylint: disable=unreachable
    return 204


async def raise_text_exception(
        scope: Scope,
        _info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    """A request handler which raises an exception with text content"""
    raise HTTPError(
        make_url(scope),
        401,
        'Unauthorized - text',
        [(b'content-type', b'text/plain')],
        None
    )
    # pylint: disable=unreachable
    return 204


async def raise_bytes_exception(
        scope: Scope,
        _info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    """A request handler which raises an exception with bytes content"""
    raise HTTPError(
        make_url(scope),
        401,
        b'Unauthorized - bytes',
        [(b'content-type', b'text/plain')],
        None
    )
    # pylint: disable=unreachable
    return 204


async def raise_writer_exception(
        scope: Scope,
        _info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    """A request handler which raises an exception with a writer content"""
    raise HTTPError(
        make_url(scope),
        401,
        text_writer('Unauthorized - writer'),
        [(b'content-type', b'text/plain')],
        None
    )
    # pylint: disable=unreachable
    return 200, [(b'content-type', b'text/plain')], text_writer('This is not a test')


if __name__ == "__main__":
    html_filename = pkg_resources.resource_filename(__name__, "exceptions.html")
    with open(html_filename, 'rt') as file_ptr:
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

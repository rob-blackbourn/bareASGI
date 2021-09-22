"""Tests for middleware"""

from bareasgi.types import HttpChainedCallback
import pytest
from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    HttpRequest,
    HttpResponse,
    text_reader,
    text_writer
)
from bareasgi.middleware import mw
from .mock_io import MockIO


@pytest.mark.asyncio
async def test_middleware():

    async def first_middleware(request: HttpRequest, handler: HttpChainedCallback) -> HttpResponse:
        request.info['path'].append('first')
        response = await handler(request)
        return response

    async def second_middleware(request: HttpRequest, handler: HttpChainedCallback) -> HttpResponse:
        request.info['path'].append('second')
        response = await handler(request)
        return response

    async def http_request_callback(request: HttpRequest) -> HttpResponse:
        request.info['path'].append('handler')
        return HttpResponse(
            200,
            [(b'content-type', b'text/plain')],
            text_writer('test')
        )

    request = mw(
        first_middleware,
        second_middleware,
        handler=http_request_callback
    )

    data = {'path': []}
    status, headers, content, push_responses = await request({}, data, {}, None)
    assert status == 200
    assert data['path'] == ['first', 'second', 'handler']
    assert headers == [(b'content-type', b'text/plain')]
    text = await text_reader(content)
    assert text == 'test'
    assert push_responses is None

"""Tests for middleware"""

import pytest
from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    text_reader,
    text_writer
)
from bareasgi.middleware import mw
from .mock_io import MockIO


@pytest.mark.asyncio
async def test_middleware():

    async def first_middleware(scope, info, matches, content, handler):
        info['path'].append('first')
        response = await handler(scope, info, matches, content)
        return response

    async def second_middleware(scope, info, matches, content, handler):
        info['path'].append('second')
        response = await handler(scope, info, matches, content)
        return response

    async def http_request_callback(scope, info, matches, content):
        info['path'].append('handler')
        return 200, [(b'content-type', b'text/plain')], text_writer('test'), None

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

"""Tests for middleware"""

import pytest

from bareasgi import (
    HttpRequest,
    HttpResponse,
    HttpRequestCallback,
    text_reader,
    text_writer
)
from bareasgi.http import make_middleware_chain


@pytest.mark.asyncio
async def test_middleware():

    async def first_middleware(
        request: HttpRequest,
        handler: HttpRequestCallback,
    ) -> HttpResponse:
        request.info['path'].append('first')
        response = await handler(request)
        return response

    async def second_middleware(
            request: HttpRequest,
            handler: HttpRequestCallback,
    ) -> HttpResponse:
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

    chain = make_middleware_chain(
        first_middleware,
        second_middleware,
        handler=http_request_callback
    )

    data = {'path': []}
    response = await chain(HttpRequest({}, data, {}, {}, None))
    assert response.status == 200
    assert data['path'] == ['first', 'second', 'handler']
    assert response.headers == [(b'content-type', b'text/plain')]
    text = await text_reader(response.body)
    assert text == 'test'
    assert response.pushes is None

"""Tests for basic functionality"""

from bareutils.streaming import bytes_reader, bytes_writer
import pytest
from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    text_writer
)
from .mock_io import MockIO


@pytest.mark.asyncio
async def test_get_text_plain():
    # noinspection PyUnusedLocal
    async def http_request_callback(_request: HttpRequest) -> HttpResponse:
        return HttpResponse(
            200,
            [(b'content-type', b'text/plain')],
            text_writer('This is not a test')
        )

    app = Application()
    app.http_router.add({'GET'}, '/{path}', http_request_callback)

    io = MockIO()
    await io.write({
        'type': 'http.request',
        'body': b'',
        'more_body': False,
    })
    await io.write({
        'type': 'http.disconnect',
    })

    _instance = await app(
        {
            'type': 'http',  # Optional but not empty: 'http' or 'https'.
            'http_version': '1.1',  # One of: '1.0', '1.1', '2'.
            'method': 'GET',  # Always uppercase.
            'scheme': 'http',  # Optional, but not empty.
            'path': '/foo',  # Decoded
            'query_string': b'',
            'root_path': "",
            # Headers must be lower cased.
            'headers': [(b'accept', b'text/plain')],
            'client': ('127.0.0.1', 36432),  # Optional, defaults to None.
            'server': ('127.0.0.1', 5000),  # Optional, defaults to None.
        },
        io.receive,
        io.send
    )

    start_response = await io.read()
    assert start_response['type'] == 'http.response.start'
    assert start_response['status'] == 200
    assert start_response['headers'] == [(b'content-type', b'text/plain')]

    body_response = await io.read()
    assert body_response['type'] == 'http.response.body'
    assert body_response['body'].decode() == "This is not a test"
    assert not body_response['more_body']


@pytest.mark.asyncio
async def test_read_request_body():
    # noinspection PyUnusedLocal
    async def http_request_callback(request: HttpRequest) -> HttpResponse:
        body = await bytes_reader(request.body)
        return HttpResponse(
            200,
            [(b'content-type', b'text/plain')],
            bytes_writer(body)
        )

    app = Application()
    app.http_router.add({'GET'}, '/{path}', http_request_callback)

    io = MockIO()
    await io.write({
        'type': 'http.request',
        'body': b'First',
        'more_body': True,
    })
    await io.write({
        'type': 'http.request',
        'body': b'Second',
        'more_body': True,
    })
    await io.write({
        'type': 'http.request',
        'body': b'Third',
        'more_body': False,
    })
    await io.write({
        'type': 'http.disconnect',
    })

    _instance = await app(
        {
            'type': 'http',  # Optional but not empty: 'http' or 'https'.
            'http_version': '1.1',  # One of: '1.0', '1.1', '2'.
            'method': 'GET',  # Always uppercase.
            'scheme': 'http',  # Optional, but not empty.
            'path': '/foo',  # Decoded
            'query_string': b'',
            'root_path': "",
            # Headers must be lower cased.
            'headers': [(b'accept', b'text/plain')],
            'client': ('127.0.0.1', 36432),  # Optional, defaults to None.
            'server': ('127.0.0.1', 5000),  # Optional, defaults to None.
        },
        io.receive,
        io.send
    )

    start_response = await io.read()
    assert start_response['type'] == 'http.response.start'
    assert start_response['status'] == 200
    assert start_response['headers'] == [(b'content-type', b'text/plain')]

    body_response = await io.read()
    assert body_response['type'] == 'http.response.body'
    assert body_response['body'] == b"FirstSecondThird"
    assert not body_response['more_body']


@pytest.mark.asyncio
async def test_chunked_response_body():
    # noinspection PyUnusedLocal
    async def http_request_callback(request: HttpRequest) -> HttpResponse:
        body = await bytes_reader(request.body)
        return HttpResponse(
            200,
            [(b'content-type', b'text/plain')],
            bytes_writer(b'aaabbbccc', chunk_size=3)
        )

    app = Application()
    app.http_router.add({'GET'}, '/{path}', http_request_callback)

    io = MockIO()
    await io.write({
        'type': 'http.request',
        'body': b'',
        'more_body': False,
    })
    await io.write({
        'type': 'http.disconnect',
    })

    _instance = await app(
        {
            'type': 'http',  # Optional but not empty: 'http' or 'https'.
            'http_version': '1.1',  # One of: '1.0', '1.1', '2'.
            'method': 'GET',  # Always uppercase.
            'scheme': 'http',  # Optional, but not empty.
            'path': '/foo',  # Decoded
            'query_string': b'',
            'root_path': "",
            # Headers must be lower cased.
            'headers': [(b'accept', b'text/plain')],
            'client': ('127.0.0.1', 36432),  # Optional, defaults to None.
            'server': ('127.0.0.1', 5000),  # Optional, defaults to None.
        },
        io.receive,
        io.send
    )

    start_response = await io.read()
    assert start_response['type'] == 'http.response.start'
    assert start_response['status'] == 200
    assert start_response['headers'] == [(b'content-type', b'text/plain')]

    body_response = await io.read()
    assert body_response['type'] == 'http.response.body'
    assert body_response['body'] == b"aaa"
    assert body_response['more_body']

    body_response = await io.read()
    assert body_response['type'] == 'http.response.body'
    assert body_response['body'] == b"bbb"
    assert body_response['more_body']

    body_response = await io.read()
    assert body_response['type'] == 'http.response.body'
    assert body_response['body'] == b"ccc"
    assert not body_response['more_body']


@pytest.mark.asyncio
async def test_empty_response_body():
    # noinspection PyUnusedLocal
    async def http_request_callback(_request: HttpRequest) -> HttpResponse:
        return HttpResponse(200)

    app = Application()
    app.http_router.add({'GET'}, '/{path}', http_request_callback)

    io = MockIO()
    await io.write({
        'type': 'http.request',
        'body': b'',
        'more_body': False,
    })
    await io.write({
        'type': 'http.disconnect',
    })

    _instance = await app(
        {
            'type': 'http',  # Optional but not empty: 'http' or 'https'.
            'http_version': '1.1',  # One of: '1.0', '1.1', '2'.
            'method': 'GET',  # Always uppercase.
            'scheme': 'http',  # Optional, but not empty.
            'path': '/foo',  # Decoded
            'query_string': b'',
            'root_path': "",
            # Headers must be lower cased.
            'headers': [(b'accept', b'text/plain')],
            'client': ('127.0.0.1', 36432),  # Optional, defaults to None.
            'server': ('127.0.0.1', 5000),  # Optional, defaults to None.
        },
        io.receive,
        io.send
    )

    start_response = await io.read()
    assert start_response['type'] == 'http.response.start'
    assert start_response['status'] == 200
    assert start_response['headers'] == []

    body_response = await io.read()
    assert body_response['type'] == 'http.response.body'
    assert body_response['body'] == b""
    assert not body_response['more_body']

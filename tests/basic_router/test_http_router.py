from datetime import datetime
from bareasgi import (
    HttpRequest,
    HttpResponse
)
from bareasgi.application import DEFAULT_NOT_FOUND_RESPONSE
from bareasgi.basic_router import BasicHttpRouter


async def ok_handler(_request: HttpRequest) -> HttpResponse:
    """Return OK"""
    return HttpResponse(200)


def test_literal_paths():
    """Test for literal paths"""
    basic_route_handler = BasicHttpRouter(DEFAULT_NOT_FOUND_RESPONSE)
    basic_route_handler.add({'GET'}, '/foo/bar/grum', ok_handler)

    handler, matches = basic_route_handler.resolve('GET', '/foo/bar/grum')
    assert handler is ok_handler
    assert matches == {}


def test_literal_path_with_trailing_slash():
    """Test for literal path with trailing slash"""
    basic_route_handler = BasicHttpRouter(DEFAULT_NOT_FOUND_RESPONSE)
    basic_route_handler.add({'GET'}, '/foo/bar/grum/', ok_handler)

    handler, matches = basic_route_handler.resolve('GET', '/foo/bar/grum/')
    assert handler is ok_handler
    assert matches == {}


def test_variable_paths():
    """Test for path including a variable"""
    basic_route_handler = BasicHttpRouter(DEFAULT_NOT_FOUND_RESPONSE)
    basic_route_handler.add({'GET'}, '/foo/{name}/grum', ok_handler)

    handler, matches = basic_route_handler.resolve('GET', '/foo/bar/grum')
    assert handler is ok_handler
    assert 'name' in matches
    assert matches['name'] == 'bar'


def test_variable_path_with_type():
    """Test for path with typed variable"""
    basic_route_handler = BasicHttpRouter(DEFAULT_NOT_FOUND_RESPONSE)
    basic_route_handler.add({'GET'}, '/foo/{id:int}/grum', ok_handler)

    handler, matches = basic_route_handler.resolve('GET', '/foo/123/grum')
    assert handler is ok_handler
    assert 'id' in matches
    assert matches['id'] == 123


def test_variable_path_with_type_and_format():
    """Test for path with typed variable and format"""
    basic_route_handler = BasicHttpRouter(DEFAULT_NOT_FOUND_RESPONSE)
    basic_route_handler.add(
        {'GET'}, '/foo/{date_of_birth:datetime:%Y-%m-%d}/grum', ok_handler)

    handler, matches = basic_route_handler.resolve(
        'GET', '/foo/2001-12-31/grum')
    assert handler is ok_handler
    assert 'date_of_birth' in matches
    assert matches['date_of_birth'] == datetime(2001, 12, 31)


def test_path_type():
    """Test for path type"""
    basic_route_handler = BasicHttpRouter(DEFAULT_NOT_FOUND_RESPONSE)
    basic_route_handler.add({'GET'}, '/ui/{rest:path}', ok_handler)

    handler, matches = basic_route_handler.resolve('GET', '/ui/index.html')
    assert handler is ok_handler
    assert 'rest' in matches
    assert matches['rest'] == 'index.html'

    handler, matches = basic_route_handler.resolve('GET', '/ui/')
    assert handler is ok_handler
    assert 'rest' in matches
    assert matches['rest'] == ''

    handler, matches = basic_route_handler.resolve(
        'GET', '/ui/folder/other.html')
    assert handler is ok_handler
    assert 'rest' in matches
    assert matches['rest'] == 'folder/other.html'

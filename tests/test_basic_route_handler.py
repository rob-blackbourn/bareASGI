from datetime import datetime
from bareasgi.basic_route_handler import BasicHttpRouteHandler
from bareasgi.types import Scope, Info, RouteMatches, Content, Reply


async def dummy_http_handler(scope: Scope, info: Info, matches: RouteMatches, content: Content, reply: Reply) -> None:
    pass


def test_literal_paths():
    basic_route_handler = BasicHttpRouteHandler()
    basic_route_handler.add({'GET'}, '/foo/bar/grum', dummy_http_handler)

    handler, matches = basic_route_handler({'method': 'GET', 'path': '/foo/bar/grum'})
    assert handler is not None


def test_literal_path_with_trailing_slash():
    basic_route_handler = BasicHttpRouteHandler()
    basic_route_handler.add({'GET'}, '/foo/bar/grum/', dummy_http_handler)

    handler, matches = basic_route_handler({'method': 'GET', 'path': '/foo/bar/grum/'})
    assert handler is not None


def test_variable_paths():
    basic_route_handler = BasicHttpRouteHandler()
    basic_route_handler.add({'GET'}, '/foo/{name}/grum', dummy_http_handler)

    handler, matches = basic_route_handler({'method': 'GET', 'path': '/foo/bar/grum'})
    assert handler is not None
    assert 'name' in matches
    assert matches['name'] == 'bar'


def test_variable_path_with_type():
    basic_route_handler = BasicHttpRouteHandler()
    basic_route_handler.add({'GET'}, '/foo/{id:int}/grum', dummy_http_handler)

    handler, matches = basic_route_handler({'method': 'GET', 'path': '/foo/123/grum'})
    assert handler is not None
    assert 'id' in matches
    assert matches['id'] == 123


def test_variable_path_with_type_and_format():
    basic_route_handler = BasicHttpRouteHandler()
    basic_route_handler.add({'GET'}, '/foo/{date_of_birth:datetime:%Y-%m-%d}/grum', dummy_http_handler)

    handler, matches = basic_route_handler({'method': 'GET', 'path': '/foo/2001-12-31/grum'})
    assert handler is not None
    assert 'date_of_birth' in matches
    assert matches['date_of_birth'] == datetime(2001, 12, 31)

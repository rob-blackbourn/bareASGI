from datetime import datetime
from bareasgi.basic_route_handler import BasicRouteHandler
from bareasgi.types import Scope, RouteMatches, Content, Reply


async def dummy_http_handler(scope: Scope, matches: RouteMatches, content: Content, reply: Reply) -> None:
    pass


def test_literal_paths():
    basic_route_handler = BasicRouteHandler()
    basic_route_handler.add_route(dummy_http_handler, '/foo/bar/grum', {'GET'}, {'http', 'https'})

    handler, matches = basic_route_handler.match('http', 'GET', '/foo/bar/grum')
    assert handler is not None


def test_literal_path_with_trailing_slash():
    basic_route_handler = BasicRouteHandler()
    basic_route_handler.add_route(lambda x: x, '/foo/bar/grum/', {'GET'}, {'http', 'https'})

    handler, matches = basic_route_handler.match('http', 'GET', '/foo/bar/grum/')
    assert handler is not None


def test_variable_paths():
    basic_route_handler = BasicRouteHandler()
    basic_route_handler.add_route(lambda x: x, '/foo/{name}/grum', {'GET'}, {'http', 'https'})

    handler, matches = basic_route_handler.match('http', 'GET', '/foo/bar/grum')
    assert handler is not None
    assert 'name' in matches
    assert matches['name'] == 'bar'


def test_variable_path_with_type():
    basic_route_handler = BasicRouteHandler()
    basic_route_handler.add_route(lambda x: x, '/foo/{id:int}/grum', {'GET'}, {'http', 'https'})

    handler, matches = basic_route_handler.match('http', 'GET', '/foo/123/grum')
    assert handler is not None
    assert 'id' in matches
    assert matches['id'] == 123


def test_variable_path_with_type_and_format():
    basic_route_handler = BasicRouteHandler()
    basic_route_handler.add_route(lambda x: x, '/foo/{date_of_birth:datetime:%Y-%m-%d}/grum', {'GET'},
                                  {'http', 'https'})

    handler, matches = basic_route_handler.match('http', 'GET', '/foo/2001-12-31/grum')
    assert handler is not None
    assert 'date_of_birth' in matches
    assert matches['date_of_birth'] == datetime(2001, 12, 31)

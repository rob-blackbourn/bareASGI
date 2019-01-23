from bareasgi.types import Scope, RouteMatches, Content, Reply
from bareasgi.http_instance import text_reader, text_writer
from bareasgi.application import Application


async def handle_any_http_route(scope: Scope, matches: RouteMatches, content: Content, reply: Reply) -> None:
    print('Start', scope, matches)
    text = await text_reader(content)
    print(text)
    await reply(200, [(b'content-type', b'text/plain')], text_writer('This is not a test'))
    print('End')


async def handle_any_websocket_route(scope: Scope, matches: RouteMatches, content: Content, response: Reply) -> None:
    print('Start', scope, matches)
    text = await text_reader(content)
    await response(200, [(b'content-type', b'text/plain')], text_writer('This is not a test'))
    print('End')


if __name__ == "__main__":
    import uvicorn
    from bareasgi import BasicRouteHandler

    route_handler = BasicRouteHandler()
    route_handler.add(handle_any_http_route, '/{path}', {'GET', 'POST', 'PUT', 'DELETE'}, {'http', 'https'})
    route_handler.add(handle_any_websocket_route, '/{path}', {'UPGRADE'}, {'ws', 'wss'})

    app = Application(route_handler)
    uvicorn.run(app, port=9009)

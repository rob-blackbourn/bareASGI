from bareasgi import Application, text_reader, text_writer
from bareasgi.http_instance import HttpRequest
from bareasgi.websocket_instance import WebSocketRequest


async def handle_any_http_route(request: HttpRequest) -> None:
    print('Start', request.scope, request.matches)
    text = await text_reader(request.content)
    print(text)
    await request.reply(200, [(b'content-type', b'text/plain')], text_writer('This is not a test'))
    print('End')


async def handle_any_websocket_route(request: WebSocketRequest) -> None:
    print('End')


if __name__ == "__main__":
    import uvicorn
    from bareasgi import BasicRouteHandler

    route_handler = BasicRouteHandler()
    route_handler.add(handle_any_http_route, '/{path}', {'GET', 'POST', 'PUT', 'DELETE'}, {'http', 'https'})
    route_handler.add(handle_any_websocket_route, '/{path}', {'UPGRADE'}, {'ws', 'wss'})

    app = Application(route_handler)
    uvicorn.run(app, port=9009)

"""
A Websocket example.
"""

import logging

import pkg_resources
import uvicorn

import bareutils.header as header

from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    WebSocketRequest,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)


async def index(_request: HttpRequest) -> HttpResponse:
    """Redirect to the test page"""
    return HttpResponse(303, [(b'Location', b'/websocket_page')])


async def websocket_page(request: HttpRequest) -> HttpResponse:
    """Send the page with the example web socket"""
    scheme = 'wss' if request.scope['scheme'] == 'https' else 'ws'
    if request.scope['http_version'] in ('2', '2.0'):
        authority = header.find(
            b':authority', request.scope['headers']).decode('ascii')
    else:
        host, port = request.scope['server']
        authority = f'{host}:{port}'
    web_socket_url = f"{scheme}://{authority}/websocket_handler"
    print(web_socket_url)

    page = request.info['html'].replace('WEB_SOCKET_URL', web_socket_url)
    return HttpResponse(200, [(b'content-type', b'text/html')], text_writer(page))


async def websocket_handler(request: WebSocketRequest) -> None:
    """The websocket callback handler"""
    await request.web_socket.accept()

    try:
        while True:
            text = await request.web_socket.receive()
            if text is None:
                break
            await request.web_socket.send('You said: ' + text)
    except Exception as error:  # pylint: disable=broad-except
        print(error)

    await request.web_socket.close()


if __name__ == "__main__":

    html_filename = pkg_resources.resource_filename(__name__, "web_socket.html")
    with open(html_filename, 'rt', encoding='utf-8') as file_ptr:
        html = file_ptr.read()
    app = Application(info=dict(html=html))

    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/websocket_page', websocket_page)

    app.ws_router.add('/websocket_handler', websocket_handler)

    uvicorn.run(app, port=9009)

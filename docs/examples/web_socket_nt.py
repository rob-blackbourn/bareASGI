import logging

import pkg_resources
import uvicorn

import bareutils.header as header

from bareasgi import Application, text_writer

logging.basicConfig(level=logging.DEBUG)


async def index(scope, info, matches, content):
    return 303, [(b'Location', b'/websocket_page')]


async def websocket_page(scope, info, matches, content):
    scheme = 'wss' if scope['scheme'] == 'https' else 'ws'
    if scope['http_version'] in ('2', '2.0'):
        authority = header.find(
            b':authority', scope['headers']).decode('ascii')
    else:
        host, port = scope['server']
        authority = f'{host}:{port}'
    web_socket_url = f"{scheme}://{authority}/websocket_handler"
    print(web_socket_url)

    page = info['html'].replace('WEB_SOCKET_URL', web_socket_url)
    return 200, [(b'content-type', b'text/html')], text_writer(page)


async def websocket_handler(scope, info, matches, web_socket):
    await web_socket.accept()

    try:
        while True:
            text = await web_socket.receive()
            if text is None:
                break
            await web_socket.send('You said: ' + text)
    except Exception as error:  # pylint: disable=broad-except
        print(error)

    await web_socket.close()


html_filename = pkg_resources.resource_filename(__name__, "web_socket.html")
with open(html_filename, 'rt') as file_ptr:
    html = file_ptr.read()
app = Application(info=dict(html=html))

app.http_router.add({'GET'}, '/', index)
app.http_router.add({'GET'}, '/websocket_page', websocket_page)

app.ws_router.add('/websocket_handler', websocket_handler)

uvicorn.run(app, port=9009)

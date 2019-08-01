"""
A simple Websocket example.
"""

import asyncio
import logging
import os
import socket
import bareutils.header as header
from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    WebSocket,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)


# pylint: disable=unused-argument
async def index_redirect(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """Redirect to the index page"""
    return 303, [(b'Location', b'/index.html')]


async def index(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """The Websocket page"""

    scheme = 'wss' if scope['scheme'] == 'https' else 'ws'
    if scope['http_version'] in ('2', '2.0'):
        authority = header.find(
            b':authority', scope['headers']).decode('ascii')
    else:
        host, port = scope['server']
        authority = f'{host}:{port}'
    web_socket_url = f"{scheme}://{authority}/test/websocket"

    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Websocket Example</title>
  </head>
  <body>
    <h1>Websocket Example</h1>

    <div id="status">Connecting...</div>

    <ul id="messages"></ul>

    <form id="message-form" action="#" method="post">
      <textarea id="message" placeholder="Write your message here..." required></textarea>
      <button type="submit">Send Message</button>
      <button type="button" id="close">Close Connection</button>
    </form>

    <script language="javascript" type="text/javascript">

    window.onload = function() {{

      // Get references to elements on the page.
      var form = document.getElementById('message-form')
      var messageField = document.getElementById('message')
      var messagesList = document.getElementById('messages')
      var socketStatus = document.getElementById('status')
      var closeBtn = document.getElementById('close')

      // Create a new WebSocket.
      var socket = new WebSocket('{web_socket_url}')
  
      // Handle any errors that occur.
      socket.onerror = function(error) {{
        console.log('WebSocket Error: ' + error)
      }}

      // Show a connected message when the WebSocket is opened.
      socket.onopen = function(event) {{
        socketStatus.innerHTML = 'Connected to: ' + event.currentTarget.url
        socketStatus.className = 'open'
      }}

      // Handle messages sent by the server.
      socket.onmessage = function(event) {{
        var message = event.data
        messagesList.innerHTML += '<li class="received"><span>Received:</span>' + message + '</li>'
      }}

      // Show a disconnected message when the WebSocket is closed.
      socket.onclose = function(event) {{
        socketStatus.innerHTML = 'Disconnected from WebSocket.'
        socketStatus.className = 'closed'
      }}

      // Send a message when the form is submitted.
      form.onsubmit = function(e) {{
        e.preventDefault()

        // Retrieve the message from the textarea.
        var message = messageField.value

        // Send the message through the WebSocket.
        socket.send(message)

        // Add the message to the messages list.
        messagesList.innerHTML += '<li class="sent"><span>Sent:</span>' + message + '</li>'

        // Clear out the message field.
        messageField.value = ''

        return false
      }}

      // Close the WebSocket connection when the close button is clicked.
      closeBtn.onclick = function(e) {{
        e.preventDefault()

        // Close the WebSocket.
        socket.close()

        return false
      }}

    }}
    </script>

  </body>
</html>
""".format(web_socket_url=web_socket_url)
    return 200, [(b'content-type', b'text/html')], text_writer(html)


async def websocket_callback(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        web_socket: WebSocket
) -> None:  # pylint: disable=unused-argument
    """The websocket callback handler"""
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


if __name__ == "__main__":

    app = Application()
    app.http_router.add({'GET'}, '/', index_redirect)
    app.http_router.add({'GET'}, '/test/index.html', index)
    app.ws_router.add('/test/websocket', websocket_callback)

    import uvicorn
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    USE_UVICORN = False
    hostname = socket.gethostname()  # pylint: disable=invalid-name

    if USE_UVICORN:
        uvicorn.run(app, port=9009)
    else:
        logging.basicConfig(level=logging.DEBUG)
        config = Config()
        config.bind = ["0.0.0.0:9009"]
        config.loglevel = 'debug'
        config.certfile = os.path.expanduser(f"~/.keys/{hostname}.crt")
        config.keyfile = os.path.expanduser(f"~/.keys/{hostname}.key")
        asyncio.run(serve(app, config))

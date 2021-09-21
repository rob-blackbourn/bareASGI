"""
A Websocket example.
"""

import asyncio
import logging
import os
import socket
from typing import cast

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
    return HttpResponse(303, [(b'Location', b'/test')])


async def test_page(request: HttpRequest) -> HttpResponse:
    """Send the page with the example web socket"""
    scheme = 'wss' if request.scope['scheme'] == 'https' else 'ws'
    if request.scope['http_version'] in ('2', '2.0'):
        authority = cast(
            bytes,
            header.find(b':authority', request.scope['headers'])
        ).decode('ascii')
    else:
        host, port = request.scope['server']
        authority = f'{host}:{port}'
    web_socket_url = f"{scheme}://{authority}/test"
    print(web_socket_url)

    page = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WebSocket Example</title>
        <style>
*, *:before, *:after {{
  -moz-box-sizing: border-box;
  -webkit-box-sizing: border-box;
  box-sizing: border-box;
}}

html {{
  font-family: Helvetica, Arial, sans-serif;
  font-size: 100%;
  background: #333;
}}

#page-wrapper {{
  width: 650px;
  background: #FFF;
  padding: 1em;
  margin: 1em auto;
  border-top: 5px solid #69c773;
  box-shadow: 0 2px 10px rgba(0,0,0,0.8);
}}

h1 {{
	margin-top: 0;
}}

#status {{
  font-size: 0.9rem;
  margin-bottom: 1rem;
}}

.open {{
  color: green;
}}

.closed {{
  color: red;
}}


ul {{
  list-style: none;
  margin: 0;
  padding: 0;
  font-size: 0.95rem;
}}

ul li {{
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #EEE;
}}

ul li:first-child {{
  border-top: 1px solid #EEE;
}}

ul li span {{
  display: inline-block;
  width: 90px;
  font-weight: bold;
  color: #999;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}}

.sent {{
  background-color: #F7F7F7;
}}

.received {{}}

#message-form {{
  margin-top: 1.5rem;
}}

textarea {{
  width: 100%;
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #D9D9D9;
  border-radius: 3px;
  box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.1);
  min-height: 100px;
  margin-bottom: 1rem;
}}

button {{
  display: inline-block;
  border-radius: 3px;
  border: none;
  font-size: 0.9rem;
  padding: 0.6rem 1em;
  color: white;
  margin: 0 0.25rem;
  text-align: center;
  background: #BABABA;
  border-bottom: 1px solid #999;
}}

button[type="submit"] {{
  background: #86b32d;
  border-bottom: 1px solid #5d7d1f;
}}

button:hover {{
  opacity: 0.75;
  cursor: pointer;
}}        
        </style>
      </head>
      <body>
      
        <div id="page-wrapper">
          <h1>WebSockets Demo</h1>
  
          <div id="status">Connecting...</div>
  
          <ul id="messages"></ul>
  
          <form id="message-form" action="#" method="post">
            <textarea id="message" placeholder="Write your message here..." required></textarea>
            <button type="submit">Send Message</button>
            <button type="button" id="close">Close Connection</button>
          </form>
        </div>
        
        <script language="javascript" type="text/javascript">

window.onload = function() {{

  // Get references to elements on the page.
  var form = document.getElementById('message-form');
  var messageField = document.getElementById('message');
  var messagesList = document.getElementById('messages');
  var socketStatus = document.getElementById('status');
  var closeBtn = document.getElementById('close');


  // Create a new WebSocket.
  var socket = new WebSocket('{web_socket_url}');


  // Handle any errors that occur.
  socket.onerror = function(error) {{
    console.log('WebSocket Error: ' + error);
  }};


  // Show a connected message when the WebSocket is opened.
  socket.onopen = function(event) {{
    socketStatus.innerHTML = 'Connected to: ' + event.currentTarget.url;
    socketStatus.className = 'open';
  }};


  // Handle messages sent by the server.
  socket.onmessage = function(event) {{
    var message = event.data;
    messagesList.innerHTML += '<li class="received"><span>Received:</span>' + message + '</li>';
  }};


  // Show a disconnected message when the WebSocket is closed.
  socket.onclose = function(event) {{
    socketStatus.innerHTML = 'Disconnected from WebSocket.';
    socketStatus.className = 'closed';
  }};


  // Send a message when the form is submitted.
  form.onsubmit = function(e) {{
    e.preventDefault();

    // Retrieve the message from the textarea.
    var message = messageField.value;

    // Send the message through the WebSocket.
    socket.send(message);

    // Add the message to the messages list.
    messagesList.innerHTML += '<li class="sent"><span>Sent:</span>' + message + '</li>';

    // Clear out the message field.
    messageField.value = '';

    return false;
  }};


  // Close the WebSocket connection when the close button is clicked.
  closeBtn.onclick = function(e) {{
    e.preventDefault();

    // Close the WebSocket.
    socket.close();

    return false;
  }};

}};
        </script>
      </body>
    </html>
    """.format(web_socket_url=web_socket_url)
    return HttpResponse(
        200,
        [(b'content-type', b'text/html')],
        text_writer(page)
    )


async def test_callback(request: WebSocketRequest) -> None:
    """The websocket callback handler"""
    await request.web_socket.accept()

    try:
        while True:
            text = cast(str, await request.web_socket.receive())
            if text is None:
                break
            await request.web_socket.send('You said: ' + text)
    except Exception as error:  # pylint: disable=broad-except
        print(error)

    await request.web_socket.close()


async def test_page1(_request: HttpRequest) -> HttpResponse:
    """A simple page"""
    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Example 1</title>
  </head>
  <body>
    <h1>Example 1</h1>

    <p>This is simple<p>
  </body>
</html>

"""
    return HttpResponse(
        200,
        [(b'content-type', b'text/html')],
        text_writer(html)
    )


if __name__ == "__main__":

    app = Application()
    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/example1', test_page1)
    app.http_router.add({'GET'}, '/test', test_page)
    app.ws_router.add('/test', test_callback)

    import uvicorn
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    USE_UVICORN = False
    hostname = socket.getfqdn()  # pylint: disable=invalid-name

    if USE_UVICORN:
        uvicorn.run(app, port=9009)
    else:
        config = Config()
        config.bind = [f"{hostname}:9009"]
        config.certfile = os.path.expanduser(f"~/.keys/{hostname}.crt")
        config.keyfile = os.path.expanduser(f"~/.keys/{hostname}.key")
        asyncio.run(serve(app, config))  # type: ignore

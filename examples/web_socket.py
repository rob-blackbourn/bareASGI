import asyncio
import logging
import os
import socket
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
import bareutils.header as header

logging.basicConfig(level=logging.DEBUG)


# noinspection PyUnusedLocal
async def index(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    return 303, [(b'Location', b'/test')], None


# noinspection PyUnusedLocal
async def test_page(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    scheme = 'wss' if scope['scheme'] == 'https' else 'ws'
    host, port = scope['server']
    if scope['http_version'] == '2':
        host = header.find(b':authority', scope['headers'])

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
    """.format(web_socket_url=f"{scheme}://{host}:{port}/test")
    return 200, [(b'content-type', b'text/html')], text_writer(page)


# noinspection PyUnusedLocal
async def test_callback(scope: Scope, info: Info, matches: RouteMatches, web_socket: WebSocket) -> None:
    await web_socket.accept()

    try:
        while True:
            text = await web_socket.receive()
            if text is None:
                break
            await web_socket.send('You said: ' + text)
    except Exception as error:
        print(error)

    await web_socket.close()


# noinspection PyUnusedLocal
async def test_page1(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
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
    return 200, [(b'content-type', b'text/html')], text_writer(html)


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

    if USE_UVICORN:
        uvicorn.run(app, port=9009)
    else:
        config = Config()
        config.bind = [f"{socket.getfqdn()}:9009"]
        config.certfile = os.path.expanduser("~/.keys/ugsb-rbla01.crt")
        config.keyfile = os.path.expanduser("~/.keys/ugsb-rbla01.key")
        asyncio.run(serve(app, config))

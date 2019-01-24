from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    Reply,
    WebSocket,
    text_reader,
    text_writer
)


async def index(scope: Scope, info: Info, matches: RouteMatches, content: Content, reply: Reply) -> None:
    # await reply(303, [[b'Location', b'http://127.0.0.1:9009/time']])
    await reply(303, [[b'Location', b'/time']])


async def time_page(scope: Scope, info: Info, matches: RouteMatches, content: Content, reply: Reply) -> None:
    page = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Time</title>
      </head>
      <body>
        <script language="javascript" type="text/javascript">

          var wsUri = "{web_socket_url}";
          var output;

          function init() {{
            output = document.getElementById("output");
            testWebSocket();
          }}

          function testWebSocket() {{
            websocket = new WebSocket(wsUri);
            websocket.onopen = function(evt) {{ onOpen(evt) }};
            websocket.onclose = function(evt) {{ onClose(evt) }};
            websocket.onmessage = function(evt) {{ onMessage(evt) }};
            websocket.onerror = function(evt) {{ onError(evt) }};
          }}

          function onOpen(evt) {{
            writeToScreen("CONNECTED");
            doSend("WebSocket rocks");
          }}

          function onClose(evt) {{
            writeToScreen("DISCONNECTED");
          }}

          function onMessage(evt) {{
            writeToScreen('<span style="color: blue;">RESPONSE: ' + evt.data+'</span>');
            websocket.close();
          }}

          function onError(evt) {{
            writeToScreen('<span style="color: red;">ERROR:</span> ' + evt.data);
          }}

          function doSend(message) {{
            writeToScreen("SENT: " + message);
            websocket.send(message);
          }}

          function writeToScreen(message) {{
            var pre = document.createElement("p");
            pre.style.wordWrap = "break-word";
            pre.innerHTML = message;
            output.appendChild(pre);
          }}

          window.addEventListener("load", init, false);
        </script>

        <h2>WebSocket Test</h2>

        <div id="output"></div>
      </body>
    </html>
    """.format(web_socket_url=f"ws://{scope['server'][0]}:{scope['server'][1]}/time")
    await reply(200, [(b'content-type', b'text/html')], text_writer(page))


async def time_callback(scope: Scope, info: Info, matches: RouteMatches, web_socket: WebSocket) -> None:
    await web_socket.accept()
    text = await web_socket.receive()
    await web_socket.send('You said: ' + text)
    await web_socket.close()


if __name__ == "__main__":
    import uvicorn

    app = Application()
    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/time', time_page)
    app.ws_router.add('/time', time_callback)

    # app.ws_route_handler.add('/{path}', web_socket_request_callback)

    uvicorn.run(app, port=9009)

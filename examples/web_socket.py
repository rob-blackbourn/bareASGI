import json
import pytz

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


async def time_zones(scope: Scope, info: Info, matches: RouteMatches, content: Content, reply: Reply) -> None:
    time_zones = json.dumps(pytz.common_timezones)
    await reply(200, [(b'content-type', b'application/json')], text_writer(time_zones))


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
        <h1>Time</h1>
        <form>
          Time Zone:<br>
          <select id="timezones">
          </select>
        </form>
        <script>
          window.onload = function() {
            console.log('loaded');
            var select = document.getElementById('timezones');
            fetch('/api/time_zones')
              .then(function(response) {
                return response.json();
              })
              .then(function(time_zones) {
                for (var i = 0; i < time_zones.length; ++i) {
                  var option = document.createElement('OPTION');
                  option.value = time_zones[i];
                  var text = document.createTextNode(time_zones[i]);
                  option.appendChild(text);
                  select.appendChild(option);
                }
              });
          }
        </script>
      </body>
    </html>
    """
    await reply(200, [(b'content-type', b'text/html')], text_writer(page))


async def web_socket_request_callback(scope: Scope, info: Info, matches: RouteMatches, web_socket: WebSocket) -> None:
    print('Start', scope, info, matches, web_socket)
    print('End')


if __name__ == "__main__":
    import uvicorn

    app = Application()
    app.http_route_handler.add({'GET'}, '/', index)
    app.http_route_handler.add({'GET'}, '/api/time_zones', time_zones)
    app.http_route_handler.add({'GET'}, '/time', time_page)

    # app.ws_route_handler.add('/{path}', web_socket_request_callback)

    uvicorn.run(app, port=9009)

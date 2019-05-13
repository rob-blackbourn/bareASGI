Server Sent Events
==================

Server sent events can be implemented by providing an endpoint with an async
generator.

The following program provides an endpoint `test_page` for the html document which contains
the JavaScript code to create the `EventSource` with a url served by the `test_events`
function. This function returnes as the body an async generator which sends the
time every second. When the event souurce is closed the task will be cancelled and the
function exits.

events end

.. code-block:: python

    import asyncio
    from bareasgi import Application, text_writer
    from datetime import datetime
    import uvicorn

    async def test_page(scope, info, matches, content):
        html = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Example</title>
      </head>
      <body>
        <h1>Server Sent Events</h1>

        Time: <snap id="time"></span>

        <script>
          var eventSource = new EventSource("http://localhost:9009/events")
          eventSource.onmessage = function(event) {
            element = document.getElementById("time")
            element.innerHTML = event.data
          }
        </script>
      </body>
    </html>

    """
        return 200, [(b'content-type', b'text/html')], text_writer(html)


    async def test_events(scope, info, matches, content):

        async def send_events():
            is_cancelled = False
            while not is_cancelled:
                try:
                    yield f'data: {datetime.now()}\n\n\n'.encode('utf-8')
                    await asyncio.sleep(1)
                except asyncio.CancelledError:
                    is_cancelled = True

        headers = [
            (b'cache-control', b'no-cache'),
            (b'content-type', b'text/event-stream'),
            (b'connection', b'keep-alive')
        ]

        return 200, headers, send_events()

    app = Application()
    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/test', test_page)
    app.http_router.add({'GET'}, '/events', test_events)

    uvicorn.run(app, host='localhost', port=9009)

Note that we set the host to "localhost" to avaoid CORS errors.
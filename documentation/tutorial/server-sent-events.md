# Server Sent Events

Server sent events provide a streaming connection from the server to the
browser. These are often overlooked, as they provide less functionality than
WebSockets. However if there is not requirement for two way communication
they can be highly efficient, particularly as they work seamlessly with
HTTP/2.

The source code can be found
[here for the html](../examples/server_sent_events.html),
and [here for the python](../examples/server_sent_events_nt.py),
(and here [here](../examples/server_sent_events.py) with typing).

## The request handler

The request handler looks as follows.

```python
async def test_events(scope, info, matches, content):

    async def send_events():
        is_cancelled = False
        while not is_cancelled:
            try:
                print('Sending event')
                yield f'data: {datetime.now()}\n\n\n'.encode('utf-8')
                # Defeat buffering by giving the server a nudge.
                yield ':\n\n\n'.encode('utf-8')
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                print('Cancelled')
                is_cancelled = True
            except:  # pylint: disable=bare-except
                print('Failed')

    headers = [
        (b'cache-control', b'no-cache'),
        (b'content-type', b'text/event-stream'),
        (b'connection', b'keep-alive')
    ]

    return 200, headers, send_events()
```

The key to understanding this is the last line:
`return 200, headers, send_events()`.

The handler is returning a function which is an asynchronous iterator. If we
look at the function itself we can that it yields some text (encoded to bytes),
then sleeps for a second before continuing this activity.

The `content-type` of the data is `text/event-stream` which follows a slightly
arcane format that can be found [here](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).

Here is the javascript that consumes the data:

```html
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
      var eventSource = new EventSource("/events")
      eventSource.onmessage = function(event) {
        element = document.getElementById("time")
        element.innerHTML = event.data
      }
    </script>
  </body>
</html>
```

## What next?

Either go back to the [table of contents](index.md) or go
to the [streaming fetch](streaming-fetch.md) tutorial.

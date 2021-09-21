# Streaming Fetch

If, when reading the [server sent events](server-sent-events.md) page, you
wondered if there was a more general way of streaming data from a server, you
were right.

The source code can be found
[here for the html](../examples/streaming_fetch.html),
and [here for the python](../examples/streaming_fetch_nt.py),
(and here [here](../examples/streaming_fetch.py) with typing).

## The request handler

The request handler looks very similar to that of server sent events, except
there is no need to implement the protocol; just streaming data is fine.

```python
async def test_events(scope, info, matches, content):
    body = await text_reader(content)
    data = json.loads(body)

    async def send_events():
        is_cancelled = False
        while not is_cancelled:
            try:
                print('Sending event')
                message = {
                    'type': 'tick',
                    'data': {
                        'time': datetime.now().isoformat(),
                        'message': data['message']
                    }
                }
                line = json.dumps(message) + '\n'
                yield line.encode('utf-8')
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                print('Cancelled')
                is_cancelled = True

    headers = [
        (b'cache-control', b'no-cache'),
        (b'content-type', b'application/json'),
        (b'connection', b'keep-alive')
    ]

    return 200, headers, send_events()
```

Rather than yielding the event source protocol we simply stream JSON, with each
JSON message terminated by a newline.

Note that, unlike the event stream, we can receive POST requests which may
have a body. This allows passing more complex requests than would be feasible
with the event source.

## The client

The client code is significantly more complicated.

The core of the client side code is the streaming fetch request:

```javascript
function streamingFetch(url, message) {
  eventTarget = new FetchEventTarget(url, {
    method: "POST",
    headers: new Headers({
      accept: "application/json",
      "content-type": "application/json",
    }),
    mode: "same-origin",
    body: JSON.stringify(message),
  });

  eventTarget.addEventListener("tick", event => {
    const data = JSON.stringify(event.data);
    console.log(data);
  });
}
```

This looks line a standard fetch, but the object created acts like an event
target.

The code for `FetchEventTarget` looks as follows:

```javascript
function FetchEventTarget(input, init) {
  const eventTarget = new EventTarget();
  const textDecoder = new TextDecoder("utf-8");
  const jsonDecoder = makeJsonDecoder(input);
  const eventStream = makeWriteableEventStream(eventTarget);
  fetch(input, init)
    .then(response => {
      response.body
        .pipeThrough(new TextDecoderStream())
        .pipeThrough(jsonDecoder)
        .pipeTo(eventStream);
    })
    .catch(error => {
      eventTarget.dispatchEvent(new CustomEvent("error", { detail: error }));
    });
  return eventTarget;
}
```

Now we can see the actual `fetch` call being used, however rather than calling
`response.text` we use the `body`. The body contains a `ReadableStream`, and the
`pipe...` methods allow processing of the stream.

The `TextDecoder` is a built in class for transforming the stream for bytes to
text.

The JSON decoder looks like this:

```javascript
function makeJsonDecoder() {
  return new TransformStream({
    start(controller) {
      controller.buf = "";
      controller.pos = 0;
    },
    transform(chunk, controller) {
      controller.buf += chunk;
      while (controller.pos < controller.buf.length) {
        if (controller.buf[controller.pos] == "\n") {
          const line = controller.buf.substring(0, controller.pos);
          controller.enqueue(JSON.parse(line));
          controller.buf = controller.buf.substring(controller.pos + 1);
          controller.pos = 0;
        } else {
          ++controller.pos;
        }
      }
    },
  });
}
```

It creates the built in class `TransformStream` and splits the text supplied by
the `TextDecoder` into lines, then parses them as JSON.

The last part of the chain is the writable event stream.

```javascript
function makeWriteableEventStream(eventTarget) {
  return new WritableStream({
    start(controller) {
      eventTarget.dispatchEvent(new Event("start"));
    },
    write(message, controller) {
      eventTarget.dispatchEvent(
        new MessageEvent(message.type, { data: message.data })
      );
    },
    close(controller) {
      eventTarget.dispatchEvent(new CloseEvent("close"));
    },
    abort(reason) {
      eventTarget.dispatchEvent(new CloseEvent("abort", { reason }));
    },
  });
}
```

This is the end of the chain and it uses the built in `WriteableStream` to turn
the incoming JSON into events.

## What next?

Either go back to the [table of contents](index.md) or go
to the [compression](compression.md) tutorial.

# Middleware

Middleware is a chain of functions terminated by a request handler.

## HTTP Middleware

It can be used to add content to the request and response or to control the
calling of subsequent handlers.

An HTTP middleware callback is an async function with the following prototype.

```python
response = await fn(request, handler)
```

This is the same as an HTTP handler, with the addition of the `callback` which is
either another middleware callback or an HTTP handler.

### Simple Example

Here is a simple middleware example.

```python
import uvicorn
from bareasgi import Application, text_writer

async def first_http_middleware(request, handler):
    request.context['message'] = 'This is first the middleware. '
    response = await handler(request)
    return response


async def second_http_middleware(request, handler):
    request.context['message'] += 'This is the second middleware.'
    response = await handler(request)
    return response


async def http_request_callback(request):
    return HttpResponse(
        200,
        [(b'content-type', b'text/plain')],
        text_writer(request.context['message'])
    )


app = Application(
    middlewares=[first_http_middleware, second_http_middleware]
)
app.http_router.add({'GET'}, '/test', http_request_callback)

uvicorn.run(app, port=9009)
```

## WebSocket Middleware

WebSocket middleware is only invoked on connection, not in the subsequent WebSocket exchanges.

### Simple Example

Here is a simple middleware example.

```python
from bareasgi import WebSocketRequest, WebSocketRequestCallback

async def first_ws_middleware(
    request: WebSocketRequest,
    handler: WebSocketRequestCallback
) -> None:
    request.context['message'] = 'This is the first middleware. '
    print("first")
    await handler(request)


async def second_ws_middleware(
    request: WebSocketRequest,
    handler: WebSocketRequestCallback
) -> None:
    request.context['message'] = 'This is the second middleware. '
    print("second")
    await handler(request)

async def ws_request_callback(request: WebSocketRequest) -> None:
    await request.web_socket.accept()

    try:
        while True:
            text = cast(str, await request.web_socket.receive())
            if text is None:
                break
            await request.web_socket.send('You said: ' + text)
    except Exception as error:
        print(error)

    await request.web_socket.close()

app = Application(
    ws_middlewares=[first_ws_middleware, second_ws_middleware]
)
app.ws_router.add('/test', test_callback)
```
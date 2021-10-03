# Getting Started

Here are some examples. More can be found in the github repository
[here](https://github.com/rob-blackbourn/bareasgi/tree/master/examples).

All the examples use the [uvicorn](https://www.uvicorn.org/) server.

The is further documentation on the
[types](https://rob-blackbourn.github.io/bareTypes/)
and [utilities](https://rob-blackbourn.github.io/bareUtils/).

## Simple

Here is a trivial example which registers a single http request callback at the endpoint `/test`
and responds with the plain text `This is not a test`.

    #!python
    from bareasgi import Application, HttpResponse, text_writer
    import uvicorn

    async def http_request_callback(request):
        return HttpResponse(200, [(b'content-type', b'text/plain')], text_writer(request.info['message']))

    app = Application(info={'message': 'This is not a test'})
    app.http_router.add({'GET'}, '/test', http_request_callback)

    uvicorn.run(app, port=9009)

The callback is defined on lines 4-5.

The `request` argument is of type `HttpRequest` which has the following properties.

- `scope` is the dictionary passed straight through from the ASGI HTTP
  [connection](https://asgi.readthedocs.io/en/latest/specs/www.html#connection-scope).

- `info` is client data passed into the server on line 7. This provides a mechanism for
  passing data around the application without the need for global variables.

- `context` is a private dictionary create for the lifetime of the request, or
  chain of requests.

- `matches` contains a dictionary of the variables which matched parts
  of the request url. As this route definition contained nothing to match this will be empty.

- `body` is an asynchronous iterator which provides the content of
  the request, and is not used here.

The callback returns an `HttpResponse`. This was given a status code, a list of
headers, and a writer. The headers are supplied as a list of name-value byte
tuples. This is how the ASGI server expects them, so no extra work need be done.
The writer is an async iterator, meaning that the response supports streaming
from the ground up.

The application is created on line 7 with some client data containing the
message to send.

The route to the callback function is defined on line 8. As this in an HTTP route (rather
than a websocket route) the `http_router` is used. The first argument to the router is the set of methods
supported. These must be uppercase strings. The second argument as the path. This may contain matching
variables, but in this case is a simple absolute path. The last argument is the HTTP response
callback.

Finally the web server is started on line 10.

## Rest Server

The following example provides a simple REST service. A GET on the `/info` endpoint
returns the contents of the `info` object, while a POST overwrites the INFO object with
the contents of the body converted from json.

    #!python
    import json
    from bareasgi import Application, HttpResponse, text_reader, text_writer
    import uvicorn

    async def get_info(request):
        text = json.dumps(request.info)
        return HttpResponse(200, [(b'content-type', b'application/json')], text_writer(text))

    async def set_info(request):
        text = await text_reader(request.body)
        data = json.loads(text)
        request.info.update(data)
        return HttpResponse(204)

    app = Application(info={'name': 'Michael Caine'})
    app.http_router.add({'GET'}, '/info', get_info)
    app.http_router.add({'POST'}, '/info', set_info)

    uvicorn.run(app, port=9009)

This example demonstrates how the body can be retrieved from the request on line 10.

Note how lightweight the response (on line 13) is, with simply the 204 (success no content) returned.

## Websocket Handler

The following fragment shows a websocket callback.

    #!python
    async def websocket_callback(request):
        await request.web_socket.accept()

        try:
            while True:
                text = await request.web_socket.receive()
                if text is None:
                    break
                await request.web_socket.send('You said: ' + text)
        except Exception as error:
            print(error)

        await request.web_socket.close()

    app = Application()
    app.ws_router.add('/test', websocket_callback)

The handler takes a `request` of type `WebSocketRequest`. This provides the
following fields:

- `scope` is the dictionary passed straight through from the ASGI WebSocket
  [connection](https://asgi.readthedocs.io/en/latest/specs/www.html#websocket-connection-scope).

- `info` is client data passed into the server on line 7. This provides a mechanism for
  passing data around the application without the need for global variables.

- `context` is a private dictionary create for the lifetime of the request, or
  chain of requests.

- `matches` contains a dictionary of the variables which matched parts
  of the request url. As this route definition contained nothing to match this will be empty.

- `web_socket` holds the `WebSocket`.

The `WebSocket` object provides four methods:

- `accept` - to accept the web socket. This must be called first.
- `receive` - to read from the socket. When closed by the client `None` is returned.
- `send` - to write to the socket.
- `close` - to close the socket.

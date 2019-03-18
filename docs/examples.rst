Examples
========

Here are some examples. More can be found in the github repository
`here <https://github.com/rob-blackbourn/bareasgi/tree/master/examples>`_.

All the examples use the `uvicorn <https://www.uvicorn.org/>`_ server.

Simple
------

Here is a trivial example which registers a single http request callback at the endpoint `/test`
and responds with the plain text `This is not a test`.

.. code-block:: python
    :linenos:

    from bareasgi import Application, text_writer
    import uvicorn

    async def http_request_callback(scope, info, matches, content):
        return 200, [(b'content-type', b'text/plain')], text_writer(info['message'])

    app = Application(info={'message': 'This is not a test'})
    app.http_router.add({'GET'}, '/test', http_request_callback)

    uvicorn.run(app, port=9009)

The callback is defined on lines 4-5.

* The first argument `scope` is the dictionary passed straight through
  from the ASGI `connection <https://asgi.readthedocs.io/en/latest/specs/www.html#connection-scope>`_.

* The second argument `info` is client data passed into the server on line 7. This provides a mechanism for
  passing data around the application without the need for global variables.

* The third argument `matches` contains a dictionary of the variables which matched parts
  of the request url. As this route definition contained nothing to match this will be empty.

* The fourth and last argument `content` is an asynchronous iterator which provides the content of
  the request, and is not used here.

The callback returns three things: the status code, a list of headers, and a writer. The headers
are supplied as a list of name-value byte tuples. This is how the ASGI server expectes them, so no
extra work need be done. The writer is an async iterator, meaning that the response supports streaming
from the ground up.

The application is created on line 7 with some client data containing the message to send.

The route to the callback function is defined on line 8. As this in an HTTP route (rather
than a websocket route) the `http_router` is used. The first argument to the router is the set of methods
supported. These must be uppercase strings. The second argument as the path. This may contain matching
variables, but in this case is a simple absolute path. The last argument is the HTTP response
callback.

Finally the web server is started on line 10.

Rest Server
-----------

The following example provides a simple REST service. A GET on the `/info` andpoint
returns the contents of the `info` object, while a POST overwrites the INFO object with
the contents of the body converted from json.

.. code-block:: python
    :linenos:

    import json
    from bareasgi import Application, text_reader, text_writer
    import uvicorn

    async def get_info(scope, info, matches, content):
        text = json.dumps(info)
        return 200, [(b'content-type', b'application/json')], text_writer(text)

    async def set_info(scope, info, matches, content):
        text = await text_reader(content)
        data = json.loads(text)
        info.update(data)
        return 204, None, None

    app = Application(info={'name': 'Michael Caine'})
    app.http_router.add({'GET'}, '/info', get_info)
    app.http_router.add({'POST'}, '/info', set_info)

    uvicorn.run(app, port=9009)

This example demonstrates how the content can be retrieved from the request on line 10.

Note how lightweight the response (on line 13) is, which simply the 204 (success not content) returned.

Websocket Handler
-----------------

The following fragment shows a websocket callback.

.. code-block:: python
    :linenos:

    async def websocket_callback(scope, info, matches, web_socket):
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

    app = Application()
    app.ws_router.add('/test', websocket_callback)

The `web_socket` object supplied on line 1 provides four methods:

* accept - to accept the web socket. This must be called first.
* receive - to read from the socket. When closed by the client `None` is returned.
* send - to write to the socket.
* close - to close the socket.

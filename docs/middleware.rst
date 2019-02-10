Middleware
==========

Middleware is a chain of functions terminated by a callback.

It can be used to add content to the request and response or to control the calling of subsequent handlers.

A middleware callback is an async function with the following prototype.

.. code-block:: python

    status, headers, content = await fn(scope, info, matches, content, callback)

This is the same as an HTTP handler, with the addition of the ``callback`` which is
either another middleware callback or an HTTP handler.

Example
-------

Here is a simple middleware example.

.. code-block:: python

    import uvicorn
    from bareasgi import Application, text_writer

    async def first_middleware(scope, info, matches, content, handler):
        info['message'] = 'This is first the middleware. '
        response = await handler(scope, info, matches, content)
        return response


    async def second_middleware(scope, info, matches, content, handler):
        info['message'] += 'This is the second middleware.'
        response = await handler(scope, info, matches, content)
        return response


    async def http_request_callback(scope, info, matches, content):
        return 200, [(b'content-type', b'text/plain')], text_writer(info['message'])


    app = Application(middlewares=[first_middleware, second_middleware])
    app.http_router.add({'GET'}, '/test', http_request_callback)

    uvicorn.run(app, port=9009)

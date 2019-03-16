Examples
========

Here are some examples. More can be found in the github repository
`here <https://github.com/rob-blackbourn/bareasgi/tree/master/examples>`_.

Simple
------

.. code-block:: python

    import logging
    from bareasgi import (
        Application,
        Scope,
        Info,
        RouteMatches,
        Content,
        HttpResponse,
        text_writer
    )

    logging.basicConfig(level=logging.DEBUG)


    async def http_request_callback(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
        return 200, [(b'content-type', b'text/plain')], text_writer('This is not a test')


    if __name__ == "__main__":
        import uvicorn

        app = Application()
        app.http_router.add({'GET'}, '/{rest:path}', http_request_callback)

        uvicorn.run(app, port=9009)


Rest Server
-----------

.. code-block:: python

    import json
    import logging
    from bareasgi import (
        Application,
        Scope,
        Info,
        RouteMatches,
        Content,
        HttpResponse,
        text_reader,
        text_writer
    )

    logging.basicConfig(level=logging.DEBUG)


    async def get_info(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
        text = json.dumps(info)
        return 200, [(b'content-type', b'application/json')], text_writer(text)


    async def set_info(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
        text = await text_reader(content)
        data = json.loads(text)
        info.update(data)
        return 204, None, None


    if __name__ == "__main__":
        import uvicorn

        app = Application(info={'name': 'Michael Caine'})
        app.http_router.add({'GET'}, '/info', get_info)
        app.http_router.add({'POST'}, '/info', set_info)

        uvicorn.run(app, port=9009)


Websocket Handler
-----------------

.. code-block:: python

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


    if __name__ == "__main__":
        import uvicorn

        app = Application()
        app.ws_router.add('/test', test_callback)

        # app.ws_route_handler.add('/{path}', web_socket_request_callback)

        uvicorn.run(app, port=9009)

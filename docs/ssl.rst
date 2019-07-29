SSL/HTTPS
=========

Overview
--------

The following describes how to start some ASGI servers supporting SSL/HTTPS.

You can find information on creating self signed certificates `here <https://medium.com/@rob.blackbourn/how-to-use-cfssl-to-create-self-signed-certificates-d55f76ba5781>`_.

Uvicorn
-------

.. code-block:: python

    import uvicorn

    ...

    uvicorn.run(
        app,
        host='127.0.0.1',
        port=8008,
        ssl_keyfile='foo.key',
        ssl_certfile='foo.crt'
    )

Hypercorn
---------

.. code-block:: python

    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    ...

    config = hypercorn.Config()
    config.bind = [ '0.0.0.0:8008' ]
    config.keyfile = 'foo.key'
    config.certfile = 'foo.crt'

    asyncio.run(serve(app, web_config))


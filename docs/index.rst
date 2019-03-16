Lightweight ASGI Web Framework
==============================

This is a web framework for :doc:`ASGI </asgi>` servers in Python 3.7.

The goal is to provide a minimal implementation, with other facilities (serving static files, CORS, sessions, etc.)
being implemented by optional packages in an attempt to keep the implementation clear and lightweight.

Usage
-----

The following trival example uses the `uvicorn <https://www.uvicorn.org/>`_ server. See :doc:`here </examples>`
for more.

.. code-block:: python

    import uvicorn
    import json
    from bareasgi import Application, text_reader, text_writer

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


The above example demonstrates some of the key features of this implementation.

* All the handler arguments are simple Python objects (list, dict, tuple, etc).
* Arguments like ``scope`` are passed directly from the ASGI server without being processed into helper classes.
* All features (even JSON encoding) are the responsibility of the application, not the framework.
* Handlers are asynchronous. The ``text_writer`` function is a simple wrapper which turns text into an async byte stream.

Installation
------------

The package can be installed with pip.

.. code-block:: bash

    pip install bareasgi

This is a Python3.7 and later package with no dependencies.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    asgi
    examples
    routing
    io
    application
    middleware
    api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

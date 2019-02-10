Handlers
========

Handlers are the callbacks invoked when a web request is made. There job is to process the request and provide a
response.

HTTP Handlers
-------------

An HTTP handler is an async function with the following prototype:

.. code-block:: python

    status, headers, writer = await fn(scope, info, matches, content)

Arguments
"""""""""

scope
    The connection scope from an ASGI `http event <https://asgi.readthedocs.io/en/latest/specs/www.html#http>`_.
    This is a dictionary containing the path, headers, etc.

info
    An application defined object for passing around global data.

matches
    A dictionary of router matches.

content
    The content of the request (if any) as an async iterable of bytes.

Results
"""""""

status
    An integer status.

headers
    A sequence of tuples of two bytes where the first is the name and the second is the value.

writer
    An async generator of bytes.

WebSocket Handlers
------------------

An WebSocket handler is an async function with the following prototype:

.. code-block:: python

    await fn(scope, info, matches, web_socket)

Arguments
"""""""""

scope
    The connection scope from an ASGI `websocket event <https://asgi.readthedocs.io/en/latest/specs/www.html#websocket>`_.
    This is a dictionary containing the path, headers, etc.

info
    An application defined object for passing around global data.

matches
    A dictionary of router matches.

web_socket
    A WebSocket class.

The WebSocket class has the following methods:

``await web_socket.accept()``
    This must be called first if it is decided to use the web socket.

``data = await web_socket.receive()``
    To receive data. The data is either a str or bytes depending on what the client sent.

``await web_socket.send(data)``
    To send data. Either a str or bytes may be sent.

``await web_socket.close()``
    To close the connection.

.. toctree::
    :maxdepth: 2
    :caption: See also:

    io.rst
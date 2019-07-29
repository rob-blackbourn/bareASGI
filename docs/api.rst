API
===

Handlers
========

Handlers are the callbacks invoked when a web request is made. There job is to process the request and provide a
response.

HTTP Handlers
-------------

An HTTP handler is an async function with the following prototype:

.. py:function:: async http_handler(scope, info, matches, content)

    :param scope: The connection scope from an ASGI `http event <https://asgi.readthedocs.io/en/latest/specs/www.html#http>`_. This is a dictionary containing the path, headers, etc.
    :type scope: Mapping[str, Any]
    :param info: An application defined object for passing around global data.
    :type info: Optional[Mapping[str, Any]]
    :param matches: A dictionary of router matches.
    :type matches: Mapping[str, Any]
    :param content: The content of the request (if any).
    :type content: AsyncIterable[bytes]
    :return: A tuple comprising: the status, the headers, and the content.
    :rtype: Tuple[int, Optional[List[Header]], Optional[AsyncGenerator[bytes, None]]]

WebSocket Handlers
------------------

An WebSocket handler is an async function with the following prototype:

.. py:function:: async websocket_handler(scope, info, matches, web_socket)

    :param scope: The connection scope from an ASGI `websocket event <https://asgi.readthedocs.io/en/latest/specs/www.html#websocket>`_. This is a dictionary containing the path, headers, etc.
    :type scope: Mapping[str, Any]
    :param info: An application defined object for passing around global data.
    :type info: Optional[Mapping[str, Any]]
    :param matches: A dictionary of router matches.
    :type matches: Mapping[str, Any]
    :param web_socket: A WebSocket class.
    :type web_socket: WebSocket

Application
-----------

.. class:: bareasgi.Application(middlewares = None, http_router = None, web_socket_router = None, startup_handlers = None, shutdown_handlers = None, not_found_response = None, info = None)

    :param middlewares: Optional list of middleware callbacks.
    :type middlewares: Optional[List[HttpMiddlewareCallback]]
    :param http_router: Optional router to for http routes.
    :type http_router: Optional[HttpRouter]
    :param web_socket_router: Optional router for web routes.
    :type web_socket_router: Optional[WebSocketRouter]
    :param startup_handlers: Optional handlers to run at startup.
    :type startup_handlers: Optional[List[StartupHandler]]
    :param shutdown_handlers: Optional handlers to run at shutdown.
    :type shutdown_handlers: Optional[List[ShutdownHandler]]
    :param info: Optional dictionary for user data.
    :type info: Optional[MutableMapping[str, Any]]

Middleware
----------

.. automodule:: bareasgi.middleware
    :members:

WebSocket
---------

.. autoclass:: bareasgi.WebSocket
    :members:
    :undoc-members:

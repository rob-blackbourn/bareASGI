"""ASGI Application"""

import logging
from typing import (
    AbstractSet,
    Any,
    Callable,
    Dict,
    List,
    Optional
)

from bareutils import text_writer

from .http import (
    HttpRouter,
    HttpResponse,
    HttpMiddlewareCallback,
    HttpRequestCallback
)
from .lifespan import LifespanRequestHandler
from .websockets import WebSocketRouter, WebSocketRequestCallback

from .basic_router import BasicHttpRouter, BasicWebSocketRouter
from .core_application import CoreApplication

LOGGER = logging.getLogger(__name__)

DEFAULT_NOT_FOUND_RESPONSE = HttpResponse(
    404,
    [(b'content-type', b'text/plain')],
    text_writer('Not Found')
)


class Application(CoreApplication):
    """A class to hold the application."""

    def __init__(
            self,
            *,
            middlewares: Optional[List[HttpMiddlewareCallback]] = None,
            http_router: Optional[HttpRouter] = None,
            web_socket_router: Optional[WebSocketRouter] = None,
            startup_handlers: Optional[List[LifespanRequestHandler]] = None,
            shutdown_handlers: Optional[List[LifespanRequestHandler]] = None,
            not_found_response: HttpResponse = DEFAULT_NOT_FOUND_RESPONSE,
            info: Optional[Dict[str, Any]] = None
    ) -> None:
        """Construct the application

        ```python
        from bareasgi import (
            Application,
            Scope,
            HttpRequest,
            HttpResponse,
            text_reader,
            text_writer
        )

        async def http_request_callback(request: HttpRequest) -> HttpResponse:
            text = await text_reader(request.body)
            return HttpResponse(
                200,
                [(b'content-type', b'text/plain')],
                text_writer('This is not a test')
            )

        import uvicorn

        app = Application()
        app.http_router.add({'GET', 'POST', 'PUT', 'DELETE'}, '/{path}', http_request_callback)

        uvicorn.run(app, port=9009)
        ```

        Args:
            middlewares (Optional[List[HttpMiddlewareCallback]], optional): Optional
                middleware callbacks. Defaults to None.
            http_router (Optional[HttpRouter], optional): Optional router to for
                http routes. Defaults to None.
            web_socket_router (Optional[WebSocketRouter], optional): Optional
                router for web routes. Defaults to None.
            startup_handlers (Optional[List[LifespanHandler]], optional): Optional
                handlers to run at startup. Defaults to None.
            shutdown_handlers (Optional[List[LifespanHandler]], optional): Optional
                handlers to run at shutdown. Defaults to None.
            not_found_response (Optional[HttpResponse], optional): Optional not
                found (404) response. Defaults to DEFAULT_NOT_FOUND_RESPONSE.
            info (Optional[Dict[str, Any]], optional): Optional
                dictionary for user data. Defaults to None.
        """
        super().__init__(
            middlewares or [],
            http_router or BasicHttpRouter(not_found_response),
            web_socket_router or BasicWebSocketRouter(),
            startup_handlers or [],
            shutdown_handlers or [],
            info or {}
        )

    def on_http_request(
            self,
            methods: AbstractSet[str],
            path: str
    ) -> Callable[[HttpRequestCallback], HttpRequestCallback]:
        """A decorator to add an http route handler to the application

        Args:
            methods (AbstractSet[str]): The http methods, e.g. {{'POST', 'PUT'}
            path (str): The path

        Returns:
            Callable[[HttpRequestCallback], HttpRequestCallback]: The decorated
                request.
        """
        def decorator(callback: HttpRequestCallback) -> Callable:
            self.http_router.add(methods, path, callback)
            return callback

        return decorator

    def on_ws_request(
            self,
            path: str
    ) -> Callable[[WebSocketRequestCallback], WebSocketRequestCallback]:
        """A decorator to add a websocket route handler to the application

        Args:
            path (str): The path

        Returns:
            Callable[[WebSocketRequestCallback], WebSocketRequestCallback]: The
                decorated handler
        """
        def decorator(
                callback: WebSocketRequestCallback
        ) -> WebSocketRequestCallback:
            self.ws_router.add(path, callback)
            return callback

        return decorator

    def on_startup(
            self,
            callback: LifespanRequestHandler
    ) -> LifespanRequestHandler:
        """A decorator to add a startup handler to the application

        Args:
            callback (LifespanRequestHandler): The startup handler.

        Returns:
            LifespanRequestHandler: The decorated handler.
        """
        self.startup_handlers.append(callback)
        return callback

    def on_shutdown(
            self,
            callback: LifespanRequestHandler
    ) -> LifespanRequestHandler:
        """A decorator to add a startup handler to the application

        Args:
            callback (LifespanRequestHandler): The shutdown handler.

        Returns:
            LifespanRequestHandler: The decorated handler.
        """
        self.shutdown_handlers.append(callback)
        return callback

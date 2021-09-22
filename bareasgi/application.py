"""
ASGI Application
"""

from typing import (
    AbstractSet,
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    MutableMapping,
    Optional,
)
import logging

from bareutils import text_writer

from .types import (
    Scope,
    HttpRouter,
    WebSocketRouter,
    LifespanHandler,
    HttpResponse,
    HttpMiddlewareCallback,
    HttpRequestCallback,
    WebSocketRequestCallback,
    Send,
    Receive
)

from .instance import Instance
from .basic_router import BasicHttpRouter, BasicWebSocketRouter

DEFAULT_NOT_FOUND_RESPONSE = HttpResponse(
    404,
    [(b'content-type', b'text/plain')],
    text_writer('Not Found')
)

LOGGER = logging.getLogger(__name__)


class Application:
    """A class to hold the application."""

    def __init__(
            self,
            *,
            middlewares: Optional[List[HttpMiddlewareCallback]] = None,
            http_router: Optional[HttpRouter] = None,
            web_socket_router: Optional[WebSocketRouter] = None,
            startup_handlers: Optional[List[LifespanHandler]] = None,
            shutdown_handlers: Optional[List[LifespanHandler]] = None,
            not_found_response: Optional[HttpResponse] = None,
            info: Optional[MutableMapping[str, Any]] = None
    ) -> None:
        """Construct the application

        ```python
        from bareasgi import (
            Application,
            Scope,
            Info,
            RouteMatches,
            Content,
            WebSocket,
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
                found (404) response. Defaults to None.
            info (Optional[MutableMapping[str, Any]], optional): Optional
                dictionary for user data. Defaults to None.
        """
        self._context: Mapping[str, Any] = {
            'info': dict() if info is None else info,
            'lifespan': {
                'lifespan.startup': startup_handlers or [],
                'lifespan.shutdown': shutdown_handlers or []
            },
            'http': {
                'router': http_router or BasicHttpRouter(
                    not_found_response or DEFAULT_NOT_FOUND_RESPONSE
                ),
                'middlewares': middlewares or []
            },
            'websocket': web_socket_router or BasicWebSocketRouter()
        }

    @property
    def info(self) -> Dict[str, Any]:
        """A place to sto application specific data.

        Returns:
            MutableMapping[str, Any]: A dictionary
        """
        return self._context['info']

    @property
    def middlewares(self) -> List[HttpMiddlewareCallback]:
        """The middlewares.

        Returns:
            List[HttpMiddlewareCallback]: A list of the middleware to apply to
                every route.
        """
        return self._context['http']['middlewares']

    @property
    def http_router(self) -> HttpRouter:
        """Router for http routes

        Returns:
            HttpRouter: The http router.
        """
        return self._context['http']['router']

    @property
    def ws_router(self) -> WebSocketRouter:
        """Router for WebSocket routes

        Returns:
            WebSocketRouter: The WebSocket router.
        """
        return self._context['websocket']

    @property
    def startup_handlers(self) -> List[LifespanHandler]:
        """Handlers run at startup

        Returns:
            List[LifespanHandler]: The startup handlers
        """
        return self._context['lifespan']['lifespan.startup']

    @property
    def shutdown_handlers(self) -> List[LifespanHandler]:
        """Handlers run on shutdown

        Returns:
            List[LifespanHandler]: The shutdown handlers.
        """
        return self._context['lifespan']['lifespan.shutdown']

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
            callback: LifespanHandler
    ) -> LifespanHandler:
        """A decorator to add a startup handler to the application

        Args:
            callback (LifespanHandler): The startup handler.

        Returns:
            LifespanHandler: The decorated handler.
        """
        self.startup_handlers.append(callback)
        return callback

    def on_shutdown(
            self,
            callback: LifespanHandler
    ) -> LifespanHandler:
        """A decorator to add a startup handler to the application

        Args:
            callback (LifespanHandler): The shutdown handler.

        Returns:
            LifespanHandler: The decorated handler.
        """
        self.shutdown_handlers.append(callback)
        return callback

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        LOGGER.debug('Creating instance', extra={'scope': scope})
        instance = Instance(self._context, scope)
        await instance(receive, send)

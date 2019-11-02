"""
ASGI Application
"""

from typing import (
    Mapping,
    Any,
    Optional,
    MutableMapping,
    List,
    AbstractSet,
    Callable
)
import logging

from baretypes import (
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
from bareutils.streaming import text_writer

from .instance import Instance
from .basic_router import BasicHttpRouter, BasicWebSocketRouter

DEFAULT_NOT_FOUND_RESPONSE: HttpResponse = (
    404,
    [(b'content-type', b'text/plain')],
    text_writer('Not Found'),
    None
)

LOGGER = logging.getLogger(__name__)


class Application:
    """A class to hold the application.

    For example:

    .. code-block:: python

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

        async def http_request_callback(
            scope: Scope,
            info: Info,
            matches: RouteMatches,
            content: Content
        ) -> HttpResponse:
            text = await text_reader(content)
            return 200, [(b'content-type', b'text/plain')], text_writer('This is not a test'), None

        import uvicorn

        app = Application()
        app.http_router.add({'GET', 'POST', 'PUT', 'DELETE'}, '/{path}', http_request_callback)

        uvicorn.run(app, port=9009)
    """

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

        :param middlewares: Optional middleware callbacks.
        :type middlewares: Optional[Sequence[HttpMiddlewareCallback]]
        :param http_router: Optional router to for http routes.
        :type http_router: Optional[HttpRouter]
        :param web_socket_router: Optional router for web routes.
        :type web_socket_router: Optional[WebSocketRouter]
        :param startup_handlers: Optional handlers to run at startup.
        :type startup_handlers: Optional[Sequence[StartupHandler]]
        :param shutdown_handlers: Optional handlers to run at shutdown.
        :type shutdown_handlers: Optional[Sequence[ShutdownHandler]]
        :param info: Optional dictionary for user data.
        :type info: Optional[MutableMapping[str, Any]]
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
    def info(self) -> MutableMapping[str, Any]:
        """A place to sto application specific data.

        :return: A dictionary.
        """
        return self._context['info']

    @property
    def middlewares(self) -> List[HttpMiddlewareCallback]:
        """The middlewares.

        :return: A list of the middleware to apply to every route.
        """
        return self._context['http']['middlewares']

    @property
    def http_router(self) -> HttpRouter:
        """Router for http routes

        :return: The configured router.
        """
        return self._context['http']['router']

    @property
    def ws_router(self) -> WebSocketRouter:
        """Router for WebSocket routes"""
        return self._context['websocket']

    @property
    def startup_handlers(self) -> List[LifespanHandler]:
        """Handlers run at startup"""
        return self._context['lifespan']['lifespan.startup']

    @property
    def shutdown_handlers(self) -> List[LifespanHandler]:
        """Handlers run on shutdown"""
        return self._context['lifespan']['lifespan.shutdown']

    def on_http_request(
            self,
            methods: AbstractSet[str],
            path: str
    ) -> Callable[[HttpRequestCallback], HttpRequestCallback]:
        """A decorator to add an http route handler to the application

        :param methods: The http mothods, e.g. {{'POST', 'PUT'}
        :type methods: AbstractSet[str]
        :param path: The path
        :type path: str
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

        :param path: The path
        :type path: str
        """
        def decorator(callback: HttpRequestCallback) -> Callable:
            self.ws_router.add(path, callback)
            return callback

        return decorator

    def on_startup(
            self,
            callback: LifespanHandler
    ) -> Callable[[LifespanHandler], LifespanHandler]:
        """A decorator to add a startup handler to the application
        """
        self.startup_handlers.append(callback)
        return callback

    def on_shutdown(
            self,
            callback: LifespanHandler
    ) -> Callable[[LifespanHandler], LifespanHandler]:
        """A decorator to add a startup handler to the application
        """
        self.shutdown_handlers.append(callback)
        return callback

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        LOGGER.debug('Creating instance', extra=scope)
        instance = Instance(self._context, scope)
        await instance(receive, send)

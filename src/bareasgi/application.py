from typing import Mapping, List, Any, Optional, MutableMapping
import logging
from .types import (
    Scope,
    ASGIInstance,
    HttpRouter,
    WebSocketRouter,
    StartupHandler,
    ShutdownHandler,
    HttpResponse,
    HttpMiddlewareCallback
)
from .instance import Instance
from .basic_router import BasicHttpRouter, BasicWebSocketRouter
from .streaming import text_writer

DEFAULT_NOT_FOUND_RESPONSE: HttpResponse = (404, [(b'content-type', b'text/plain')], text_writer('Not Found'))

logger = logging.getLogger(__name__)


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
            Reply,
            WebSocket,
            text_reader,
            text_writer
        )

        async def http_request_callback(
            scope: Scope,
            info: Info,
            matches: RouteMatches,
            content: Content,
            reply: Reply
        ) -> None:
            text = await text_reader(content)
            await reply(200, [(b'content-type', b'text/plain')], text_writer('This is not a test'))

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
            startup_handlers: Optional[List[StartupHandler]] = None,
            shutdown_handlers: Optional[List[ShutdownHandler]] = None,
            not_found_response: Optional[HttpResponse] = None,
            info: Optional[MutableMapping[str, Any]] = None
    ) -> None:
        """Construct the application

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
        """
        self._context: Mapping[str, Any] = {
            'info': info or {},
            'lifespan': {
                'lifespan.startup': startup_handlers or [],
                'lifespan.shutdown': shutdown_handlers or []
            },
            'http': {
                'router': http_router or BasicHttpRouter(not_found_response or DEFAULT_NOT_FOUND_RESPONSE),
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
    def startup_handlers(self) -> List[StartupHandler]:
        """Handlers run at startup"""
        return self._context['lifespan']['lifespan.startup']


    @property
    def shutdown_handlers(self) -> List[ShutdownHandler]:
        """Handlers run on shutdown"""
        return self._context['lifespan']['lifespan.shutdown']


    def __call__(self, scope: Scope) -> ASGIInstance:
        logger.debug('Creating instance', extra=scope)
        return Instance(self._context, scope)

"""
ASGI Application
"""

from typing import (
    AbstractSet,
    Any,
    Callable,
    Dict,
    List,
    MutableMapping,
    Optional,
    cast
)
import logging

from asgi_typing import (
    HTTPScope,
    ASGIHTTPReceiveCallable,
    ASGIHTTPSendCallable,
    LifespanScope,
    ASGILifespanReceiveCallable,
    ASGILifespanSendCallable,
    WebSocketScope,
    ASGIWebSocketReceiveCallable,
    ASGIWebSocketSendCallable,
    ASGIWebSocketReceiveEvent,
    Scope,
    ASGISendCallable,
    ASGIReceiveCallable
)
from bareutils import text_writer

from .http import (
    HttpInstance,
    HttpRouter,
    HttpResponse,
    HttpMiddlewareCallback,
    HttpRequestCallback
)
from .lifespan import LifespanRequestHandler, LifespanInstance
from .websockets import (
    WebSocketRouter,
    WebSocketRequestCallback,
    WebSocketInstance
)

from .basic_router import BasicHttpRouter, BasicWebSocketRouter

DEFAULT_NOT_FOUND_RESPONSE = HttpResponse(
    404,
    [(b'content-type', b'text/plain')],
    text_writer('Not Found')
)

LOGGER = logging.getLogger(__name__)


class CoreApplication:

    def __init__(
            self,
            middlewares: Optional[List[HttpMiddlewareCallback]] = None,
            http_router: Optional[HttpRouter] = None,
            web_socket_router: Optional[WebSocketRouter] = None,
            startup_handlers: Optional[List[LifespanRequestHandler]] = None,
            shutdown_handlers: Optional[List[LifespanRequestHandler]] = None,
            not_found_response: Optional[HttpResponse] = None,
            info: Optional[Dict[str, Any]] = None
    ) -> None:
        self.info: Dict[str, Any] = {} if info is None else info
        self.http_router = http_router or BasicHttpRouter(
            not_found_response or DEFAULT_NOT_FOUND_RESPONSE
        )
        self.middlewares = middlewares or []
        self.ws_router = web_socket_router or BasicWebSocketRouter()
        self.startup_handlers = startup_handlers
        self.shutdown_handlers = shutdown_handlers

    async def _handle_http_request(
            self,
            scope: HTTPScope,
            receive: ASGIHTTPReceiveCallable,
            send: ASGIHTTPSendCallable
    ) -> None:
        instance = HttpInstance(
            scope,
            self.http_router,
            self.middlewares,
            self.info
        )
        await instance(receive, send)

    async def _handle_lifespan_request(
            self,
            scope: LifespanScope,
            receive: ASGILifespanReceiveCallable,
            send: ASGILifespanSendCallable
    ) -> None:
        instance = LifespanInstance(
            scope,
            self.startup_handlers,
            self.shutdown_handlers,
            self.info
        )
        await instance(receive, send)

    async def _handle_websocket_request(
            self,
            scope: WebSocketScope,
            receive: ASGIWebSocketReceiveCallable,
            send: ASGIWebSocketSendCallable
    ) -> None:
        instance = WebSocketInstance(
            scope,
            self.ws_router,
            self.info
        )
        await instance(receive, send)

    async def __call__(
            self,
            scope: Scope,
            receive: ASGIReceiveCallable,
            send: ASGISendCallable
    ) -> None:
        if scope['type'] == 'http':
            await self._handle_http_request(
                cast(HTTPScope, scope),
                cast(ASGIHTTPReceiveCallable, receive),
                cast(ASGIHTTPSendCallable, send)
            )
        elif scope['type'] == 'lifespan':
            await self._handle_lifespan_request(
                cast(LifespanScope, scope),
                cast(ASGILifespanReceiveCallable, receive),
                cast(ASGILifespanSendCallable, send)
            )
        elif scope['type'] == 'websocket':
            await self._handle_websocket_request(
                cast(WebSocketScope, scope),
                cast(ASGIWebSocketReceiveEvent, receive),
                cast(ASGIWebSocketSendCallable, send)
            )
        else:
            raise ValueError('Unknown scope type: ' + scope['type'])


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
            not_found_response: Optional[HttpResponse] = None,
            info: Optional[MutableMapping[str, Any]] = None
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
                found (404) response. Defaults to None.
            info (Optional[MutableMapping[str, Any]], optional): Optional
                dictionary for user data. Defaults to None.
        """
        super().__init__(
            middlewares,
            http_router,
            web_socket_router,
            startup_handlers,
            shutdown_handlers,
            not_found_response,
            info
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

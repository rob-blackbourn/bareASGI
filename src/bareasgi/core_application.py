"""The core ASGI application"""

import logging
from typing import Any, Final, cast

from .http import (
    HTTPScope,
    ASGIHTTPReceiveCallable,
    ASGIHTTPSendCallable,
)
from .lifespan import (
    LifespanScope,
    ASGILifespanReceiveCallable,
    ASGILifespanSendCallable,
)
from .websockets.typing import (
    WebSocketScope,
    ASGIWebSocketReceiveCallable,
    ASGIWebSocketSendCallable,
)
from .typing import (
    Scope,
    ASGISendCallable,
    ASGIReceiveCallable
)

from .http import HttpInstance, HttpRouter, HttpMiddlewareCallback
from .lifespan import LifespanRequestHandler, LifespanInstance
from .websockets import (
    WebSocketRouter,
    WebSocketInstance,
    WebSocketMiddlewareCallback
)

LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


class CoreApplication:
    """The core ASGI application"""

    def __init__(
            self,
            middlewares: list[HttpMiddlewareCallback],
            http_router: HttpRouter,
            ws_middlewares: list[WebSocketMiddlewareCallback],
            ws_router: WebSocketRouter,
            startup_handlers: list[LifespanRequestHandler],
            shutdown_handlers: list[LifespanRequestHandler],
            info: dict[str, Any]
    ) -> None:
        self.info = info
        self.middlewares = middlewares
        self.http_router = http_router
        self.ws_router = ws_router
        self.ws_middlewares = ws_middlewares
        self.startup_handlers = startup_handlers
        self.shutdown_handlers = shutdown_handlers

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
        await instance.process(receive, send)

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
        await instance.process(receive, send)

    async def _handle_websocket_request(
            self,
            scope: WebSocketScope,
            receive: ASGIWebSocketReceiveCallable,
            send: ASGIWebSocketSendCallable
    ) -> None:
        instance = WebSocketInstance(
            scope,
            self.ws_router,
            self.ws_middlewares,
            self.info
        )
        await instance.process(receive, send)

    async def __call__(
            self,
            scope: Scope,
            receive: ASGIReceiveCallable,
            send: ASGISendCallable
    ) -> None:
        """This is the entrypoint to the ASGI application.

        Args:
            scope (Scope): The ASGI scope.
            receive (ASGIReceiveCallable): A coroutine to receive ASGI events.
            send (ASGISendCallable): A coroutine to send ASGI events.

        Raises:
            ValueError: For an unknown event type.
        """
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
                cast(ASGIWebSocketReceiveCallable, receive),
                cast(ASGIWebSocketSendCallable, send)
            )

        else:

            raise ValueError('Unknown event type: ' + scope['type'])

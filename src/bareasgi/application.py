from typing import Mapping, List, Any, Optional, MutableMapping
from .types import (
    Scope,
    ASGIInstance,
    HttpRouter,
    WebSocketRouter,
    StartupHandler,
    ShutdownHandler
)
from .instance import Instance
from .basic_router import BasicHttpRouter, BasicWebSocketRouter


class Application:

    def __init__(
            self,
            http_route_handler: Optional[HttpRouter] = None,
            web_socket_route_handler: Optional[WebSocketRouter] = None,
            startup_handlers: Optional[List[StartupHandler]] = None,
            shutdown_handlers: Optional[List[ShutdownHandler]] = None,
            info: Optional[MutableMapping[str, Any]] = None
    ) -> None:
        self._context: Mapping[str, Any] = {
            'info': info or {},
            'lifespan': {
                'lifespan.startup': startup_handlers or [],
                'lifespan.shutdown': shutdown_handlers or []
            },
            'http': http_route_handler or BasicHttpRouter(),
            'websocket': web_socket_route_handler or BasicWebSocketRouter()
        }


    @property
    def http_router(self) -> HttpRouter:
        return self._context['http']


    @property
    def ws_router(self) -> WebSocketRouter:
        return self._context['websocket']


    @property
    def startup_handlers(self) -> List[StartupHandler]:
        return self._context['lifespan']['lifespan.startup']


    @property
    def shutdown_handlers(self) -> List[ShutdownHandler]:
        return self._context['lifespan']['lifespan.shutdown']


    def __call__(self, scope: Scope) -> ASGIInstance:
        return Instance(self._context, scope)

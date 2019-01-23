from typing import Mapping, List, Any, Optional
from .types import (
    Scope,
    ASGIInstance,
    RouteHandler,
    StartupHandler,
    ShutdownHandler
)
from .instance import Instance
from .basic_route_handler import BasicRouteHandler


class Application:

    def __init__(
            self,
            route_handler: Optional[RouteHandler] = None,
            startup_handlers: Optional[List[StartupHandler]] = None,
            shutdown_handlers: Optional[List[ShutdownHandler]] = None
    ) -> None:
        self._context: Mapping[str, Any] = {
            'info': {},
            'lifespan': {
                'lifespan.startup': startup_handlers or [],
                'lifespan.shutdown': shutdown_handlers or []
            },
            'http': {
                'http.request': route_handler
            },
            'websocket': {
                'websocket.connect': route_handler or BasicRouteHandler()
            }
        }


    @property
    def route_handler(self) -> RouteHandler:
        return self._context['http']['http.request']


    @property
    def startup_handlers(self) -> List[StartupHandler]:
        return self._context['lifespan']['lifespan.startup']


    @property
    def shutdown_handlers(self) -> List[ShutdownHandler]:
        return self._context['lifespan']['lifespan.shutdown']


    def __call__(self, scope: Scope) -> ASGIInstance:
        return Instance(self._context, scope)

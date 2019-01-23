from __future__ import annotations
from typing import Mapping, Any
from .types import (
    Scope,
    Send,
    Receive,
    ASGIInstance,
)
from .lifespan_manager import LifespanManager
from .http_manager import HttpManager
from .websocket_manager import WebSocketManager


class Instance:
    HANDLERS = {
        'lifespan': LifespanManager,
        'http': HttpManager,
        'websocket': WebSocketManager
    }


    def __init__(self, context: Mapping[str, Any], scope: Scope):
        scope_type = scope['type']
        klass = self.HANDLERS[scope_type]
        klass_context = context.get(scope_type)
        info = context.get('info')
        self.handler = klass(scope, klass_context, info)


    async def __call__(self, receive: Receive, send: Send) -> None:
        await self.handler(receive, send)


class Application:

    def __init__(
            self,
            route_handler,
            startup_handlers=None,
            shutdown_handlers=None
    ) -> None:
        self.context = {
            'info': {},
            'lifespan': {
                'lifespan.startup': startup_handlers or [],
                'lifespan.shutdown': shutdown_handlers or []
            },
            'http': {
                'http.request': route_handler
            },
            'websocket': {
                'websocket.connect': route_handler
            }
        }


    @property
    def route_handler(self):
        return self.context['http']['http.request']


    @property
    def startup_handlers(self):
        return self.context['lifespan']['lifespan.startup']


    @property
    def shutdown_handlers(self):
        return self.context['lifespan']['lifespan.shutdown']


    def __call__(self, scope: Scope) -> ASGIInstance:
        return Instance(self.context, scope)

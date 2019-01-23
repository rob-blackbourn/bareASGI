from typing import Mapping, Callable
from .types import (
    Scope,
    Context,
    Info,
    Send,
    Receive,
    ASGIInstance
)
from .lifespan_instance import LifespanInstance
from .http_instance import HttpInstance
from .websocket_instance import WebSocketManager


class Instance:
    INSTANCES_CLASSES: Mapping[str, Callable[[Scope, Context, Info], ASGIInstance]] = {
        'lifespan': LifespanInstance,
        'http': HttpInstance,
        'websocket': WebSocketManager
    }


    def __init__(self, context: Context, scope: Scope) -> None:
        scope_type = scope['type']
        klass = self.INSTANCES_CLASSES[scope_type]
        klass_context = context.get(scope_type)
        info: Info = context.get('info')
        self.manager = klass(scope, klass_context, info)


    async def __call__(self, receive: Receive, send: Send) -> None:
        await self.manager(receive, send)

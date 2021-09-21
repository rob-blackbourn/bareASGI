"""
An instance provider.
"""

import logging
from typing import Any, Callable, Mapping

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
from .websocket_instance import WebSocketInstance

LOGGER = logging.getLogger(__name__)

InstanceFactory = Callable[[Scope, Any, Info], ASGIInstance]


class Instance:
    """An instance provider"""

    INSTANCES_CLASSES: Mapping[str, InstanceFactory] = {
        'lifespan': LifespanInstance,
        'http': HttpInstance,
        'websocket': WebSocketInstance
    }

    def __init__(self, context: Context, scope: Scope) -> None:
        """Initialise the instance provider

        Args:
            context (Context): The application context
            scope (Scope): The ASGI scope
        """
        scope_type = scope['type']
        klass = self.INSTANCES_CLASSES[scope_type]
        klass_context = context.get(scope_type)
        info: Info = context['info']
        LOGGER.debug(
            'Creating instance for "%s"',
            scope_type,
            extra={'scope': scope, 'context': context, 'info': info}
        )
        self.manager = klass(scope, klass_context, info)

    async def __call__(self, receive: Receive, send: Send) -> None:
        await self.manager(receive, send)

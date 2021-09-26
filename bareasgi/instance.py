"""
An instance provider.
"""

import logging
from typing import Any, Callable, Dict, Mapping

from .types import (
    Scope,
    Send,
    Receive,
    ASGIInstance
)

from .http import HttpInstance
from .lifespan import LifespanInstance
from .websockets import WebSocketInstance

LOGGER = logging.getLogger(__name__)

InstanceFactory = Callable[[Scope, Any, Dict[str, Any]], ASGIInstance]


class Instance:
    """An instance provider"""

    INSTANCES_CLASSES: Mapping[str, InstanceFactory] = {
        'lifespan': LifespanInstance,
        'http': HttpInstance,
        'websocket': WebSocketInstance
    }

    def __init__(self, context: Mapping[str, Any], scope: Scope) -> None:
        """Initialise the instance provider

        Args:
            context (Mapping[str, Any]): The application context
            scope (Scope): The ASGI scope
        """
        scope_type = scope['type']
        klass = self.INSTANCES_CLASSES[scope_type]
        klass_context = context.get(scope_type)
        info: Dict[str, Any] = context['info']
        LOGGER.debug(
            'Creating instance for "%s"',
            scope_type,
            extra={'scope': scope, 'context': context, 'info': info}
        )
        self.manager = klass(scope, klass_context, info)

    async def __call__(self, receive: Receive, send: Send) -> None:
        await self.manager(receive, send)

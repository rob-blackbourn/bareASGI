"""
A handler of lifecycle event requests
"""

import logging
from typing import Any, Dict, List, Mapping

from ..types import (
    Scope,
    Send,
    Receive
)

from .lifespan_request import LifespanRequest, LifespanRequestHandler

LOGGER = logging.getLogger(__name__)


class LifespanInstance:
    """An instance factor for lifespan event requests"""

    def __init__(
            self,
            scope: Scope,
            context: Mapping[str, Any],
            info: Dict[str, Any]
    ) -> None:
        """Initialise a lifespan instance.

        Args:
            scope (Scope): The ASGI scope
            context (Mapping[str, Any]): The application context
            info (Dict[str, Any]): The user provided dict
        """
        self.scope = scope
        self.context = context
        self.info = info

    async def __call__(self, receive: Receive, send: Send) -> None:
        # The lifespan scope exists for the duration of the event loop, and
        # only exits on 'lifespan.shutdown'.
        request = self.scope
        while request['type'] != 'lifespan.shutdown':
            # Fetch the lifespan request
            request = await receive()
            request_type = request['type']

            LOGGER.debug(
                'Handling request for "%s"',
                request_type,
                extra={'request': request}
            )

            try:
                # Run the handlers for this action.
                handlers: List[LifespanRequestHandler] = self.context.get(
                    request_type, [])
                for handler in handlers:
                    await handler(
                        LifespanRequest(
                            self.scope,
                            self.info,
                            request)
                    )

                # Send the response
                await send({'type': f'{request_type}.complete'})
            except Exception as error:  # pylint: disable=broad-except
                await send({
                    'type': f'{request_type}.failed',
                    'message': '{}: {}'.format(type(error).__name__, error)
                })

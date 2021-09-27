"""
A handler of lifecycle event requests
"""

import logging
from typing import Any, Dict, List, cast

from asgi_typing import (
    LifespanScope,
    ASGILifespanReceiveCallable,
    ASGILifespanSendCallable,
    LifespanShutdownCompleteEvent,
    LifespanStartupCompleteEvent,
    LifespanStartupFailedEvent,
    LifespanShutdownFailedEvent
)

from .lifespan_request import LifespanRequest, LifespanRequestHandler

LOGGER = logging.getLogger(__name__)


class LifespanInstance:
    """An instance factor for lifespan event requests"""

    def __init__(
            self,
            scope: LifespanScope,
            startup_handlers: List[LifespanRequestHandler],
            shutdown_handlers: List[LifespanRequestHandler],
            info: Dict[str, Any]
    ) -> None:
        self.scope = scope
        self.startup_handlers = startup_handlers
        self.shutdown_handlers = shutdown_handlers
        self.info = info

    async def _call_handlers(
            self,
            handlers: List[LifespanRequestHandler]
    ) -> None:
        for handler in handlers:
            await handler(
                LifespanRequest(
                    self.scope,
                    self.info
                )
            )

    async def _handle_startup_event(
            self,
            send: ASGILifespanSendCallable
    ) -> None:
        try:
            await self._call_handlers(
                self.startup_handlers
            )
            startup_complete_event: LifespanStartupCompleteEvent = {
                'type': 'lifespan.startup.complete'
            }
            await send(startup_complete_event)
        except Exception as error:  # pylint: disable=broad-except
            startup_failed_event: LifespanStartupFailedEvent = {
                'type': 'lifespan.startup.failed',
                'message': f'{type(error).__name__}: {error}'
            }
            await send(startup_failed_event)

    async def _handle_shutdown_event(
            self,
            send: ASGILifespanSendCallable
    ) -> None:
        try:
            await self._call_handlers(
                self.shutdown_handlers
            )
            shutdown_complete_event: LifespanShutdownCompleteEvent = {
                'type': 'lifespan.shutdown.complete'
            }
            await send(shutdown_complete_event)
        except Exception as error:  # pylint: disable=broad-except
            shutdown_failed_event: LifespanShutdownFailedEvent = {
                'type': 'lifespan.shutdown.failed',
                'message': f'{type(error).__name__}: {error}'
            }
            await send(shutdown_failed_event)

    async def __call__(
            self,
            receive: ASGILifespanReceiveCallable,
            send: ASGILifespanSendCallable
    ) -> None:
        # The lifespan scope exists for the duration of the event loop, and
        # only exits on 'lifespan.shutdown'.
        has_shutdown = False
        while has_shutdown:
            # Fetch the lifespan request
            event = await receive()

            LOGGER.debug(
                'Handling event for "%s"',
                event['type'],
                extra=cast(Dict[str, Any], event)
            )

            if event['type'] == 'lifespan.startup':
                await self._handle_startup_event(send)
            elif event['type'] == 'lifespan.shutdown':
                await self._handle_shutdown_event(send)
                has_shutdown = True

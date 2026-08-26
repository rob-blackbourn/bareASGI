"""A handler of lifecycle event requests"""

import logging
from typing import Any, Final

from .typing import (
    LifespanScope,
    ASGILifespanReceiveCallable,
    ASGILifespanSendCallable,
    LifespanShutdownCompleteEvent,
    LifespanStartupCompleteEvent,
    LifespanStartupFailedEvent,
    LifespanShutdownFailedEvent
)

from .request import LifespanRequest, LifespanRequestHandler

LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


class LifespanInstance:
    """An instance factor for lifespan event requests"""

    def __init__(
            self,
            scope: LifespanScope,
            startup_handlers: list[LifespanRequestHandler],
            shutdown_handlers: list[LifespanRequestHandler],
            info: dict[str, Any]
    ) -> None:
        self.scope = scope
        self.startup_handlers = startup_handlers
        self.shutdown_handlers = shutdown_handlers
        self.info = info

    async def process(
            self,
            receive: ASGILifespanReceiveCallable,
            send: ASGILifespanSendCallable
    ) -> None:
        """Process lifespan requests.

        Args:
            receive (ASGILifespanReceiveCallable): The function that receives requests.
            send (ASGILifespanSendCallable): The function that send requests.
        """
        # The lifespan scope exists for the duration of the event loop, and
        # only exits on 'lifespan.shutdown'.
        done = False
        while not done:
            # Fetch the lifespan request
            event = await receive()

            LOGGER.debug('Handling event type "%s".', event['type'])

            if event['type'] == 'lifespan.startup':
                await self._handle_startup_event(send)
            elif event['type'] == 'lifespan.shutdown':
                await self._handle_shutdown_event(send)
                done = True

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

    async def _call_handlers(
            self,
            handlers: list[LifespanRequestHandler]
    ) -> None:
        for handler in handlers:
            await handler(
                LifespanRequest(
                    self.scope,
                    self.info
                )
            )

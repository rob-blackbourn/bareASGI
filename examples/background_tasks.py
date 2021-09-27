"""
This program sets up a background task which gets gracefully shut down when the application exits.
"""

import asyncio
from asyncio import Event
from datetime import datetime
import logging

from bareasgi import (
    Application,
    LifespanRequest,
    HttpRequest,
    HttpResponse,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger('background_tasks')


async def time_ticker(shutdown_event: Event) -> None:
    """
    This is the background task. It prints the time every second until the
    cancellation event is set.

    :param shutdown_event: An event which gets set when the task is cancelled.
    """

    LOGGER.debug('Starting the time ticker')

    while not shutdown_event.is_set():
        LOGGER.debug('time: %s', datetime.now())
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=1)
        except asyncio.TimeoutError:
            LOGGER.debug(
                'Timeout - normal behaviour when waiting with a timeout')
        except:  # pylint: disable=bare-except
            LOGGER.exception('Failure - we should not see this exception')

    LOGGER.debug('The time ticker has stopped')


async def time_ticker_startup_handler(request: LifespanRequest) -> None:
    """
    This handles starting the time ticker.

    Note: the asyncio.Event object is created here. This ensures the object acquires
    the correct event loop.

    :param scope: The ASGI information about the lifespan scope.
    :param info: The application info object where data can be passed around the application.
    :param request: The lifespace request
    """

    # Create an event that can be set when the background task should shutdown.
    shutdown_event = Event()
    request.info['shutdown_event'] = shutdown_event

    # Create the background task.
    request.info['time_ticker_task'] = asyncio.create_task(
        time_ticker(shutdown_event))


async def time_ticker_shutdown_handler(request: LifespanRequest) -> None:
    """
    This handles shutting down the time ticker.

    :param scope: The ASGI information about the lifespan scope.
    :param info: The application info object where data can be passed around the application.
    :param request: The lifespace request
    """

    # Set the shutdown event so the background task can stop gracefully.
    shutdown_event: Event = request.info['shutdown_event']
    LOGGER.debug('Stopping the time_ticker')
    shutdown_event.set()

    # Wait for the background task to finish.
    time_ticker_task: asyncio.Task = request.info['time_ticker_task']
    LOGGER.debug('Waiting for time_ticker')
    await time_ticker_task
    LOGGER.debug('time_ticker shutdown')


async def http_request_callback(_request: HttpRequest) -> HttpResponse:
    """
    A Simple endpoint to demonstrate that requests can still be serviced when
    a background task is running.
    """
    return HttpResponse(
        200,
        [(b'content-type', b'text/plain')],
        text_writer('This is not a test')
    )


if __name__ == "__main__":
    import uvicorn

    # Create the application with startup and shutdown handlers.
    app = Application(
        startup_handlers=[time_ticker_startup_handler],
        shutdown_handlers=[time_ticker_shutdown_handler]
    )

    app.http_router.add({'GET'}, '/{rest:path}', http_request_callback)

    uvicorn.run(app, port=9009)

import asyncio
from asyncio import Event
from bareasgi.types import HttpRequest, HttpResponse
from datetime import datetime
import logging
import uvicorn

from bareasgi import Application, text_writer, LifespanRequest

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger('background_tasks')


async def time_ticker(info, shutdown_event):
    """
    This is the background task. It prints the time every second until the
    cancellation event is set.

    :param shutdown_event: An event which gets set when the task is cancelled.
    """

    LOGGER.debug('Starting the time ticker')

    while not shutdown_event.is_set():
        info['now'] = datetime.now()
        LOGGER.debug('time: %s', info['now'])
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=1)
        except asyncio.TimeoutError:
            LOGGER.debug(
                'Timeout - normal behaviour when waiting with a timeout')
        except:  # pylint: disable=bare-except
            LOGGER.exception('Failure - we should not see this exception')

    LOGGER.debug('The time ticker has stopped')


async def time_ticker_startup_handler(request: LifespanRequest) -> None:
    # Create an event that can be set when the background task should shutdown.
    shutdown_event = Event()
    request.info['shutdown_event'] = shutdown_event

    # Create the background task.
    request.info['time_ticker_task'] = asyncio.create_task(
        time_ticker(request.info, shutdown_event)
    )


async def time_ticker_shutdown_handler(request: LifespanRequest) -> None:
    # Set the shutdown event so the background task can stop gracefully.
    shutdown_event: Event = request.info['shutdown_event']
    LOGGER.debug('Stopping the time_ticker')
    shutdown_event.set()

    # Wait for the background task to finish.
    time_ticker_task: asyncio.Task = request.info['time_ticker_task']
    LOGGER.debug('Waiting for time_ticker')
    await time_ticker_task
    LOGGER.debug('time_ticker shutdown')


async def http_request_callback(request: HttpRequest) -> HttpResponse:
    headers = [
        (b'content-type', b'text/plain')
    ]
    return HttpResponse(
        200,
        headers,
        text_writer(f"Last time tick: {request.info.get('now')}")
    )

app = Application(
    startup_handlers=[time_ticker_startup_handler],
    shutdown_handlers=[time_ticker_shutdown_handler]
)
app.http_router.add({'GET'}, '/{rest:path}', http_request_callback)

uvicorn.run(app, port=9009)

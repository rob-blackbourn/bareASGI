# Background Tasks

Some times it is necessary to run background tasks. For example to poll a data
source, or listen to a data stream.

The following example starts a background task when the server starts up,
then gracefully terminates it when the server shuts down.

The source code for the following example can be found
[here](../examples/lifespan_nt.py)
(and here [here](../examples/lifespan.py) with typing).

## The Task

The following code provides a dummy task, which just waits for a second then
gets the time. This time I've used the typed code.

```python
async def time_ticker(info: Info, shutdown_event: Event) -> None:

    print('Starting the time ticker')

    while not shutdown_event.is_set():
        info['now'] = datetime.now()
        print(f"time: {info['now']}")

        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=1)
        except asyncio.TimeoutError:
            print('Timeout - normal behaviour when waiting with a timeout')
        except:
            print('Failure - we should not see this exception')

    print('The time ticker has stopped')
```

Rather than simply cancelling the task, I've used the asyncio
[Event](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Event)
to shutdown more gracefully.

## The Startup Handler

First we create the event and store it in the application's `info`.

Then we create the task with
[`asyncio.create_task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task)
and store the task in the application's `info`.

When the task is created it will be scheduled to run. Any time the task
*awaits*, it gives up control and other tasks which are ready to run can
proceed.

```python
async def time_ticker_startup_handler(scope, info, request):
    # Create an event that can be set when the background task should shutdown.
    shutdown_event = Event()
    info['shutdown_event'] = shutdown_event

    # Create the background task.
    info['time_ticker_task'] = asyncio.create_task(
        time_ticker(info, shutdown_event)
    )
```

Note that the shutdown event was created in the startup handler. This is
**critical**. I'll discuss why in the "Gotcha!" section.

## The Shutdown Handler

Here is the code for the shutdown handler.

```python
async def time_ticker_shutdown_handler(scope, info, request):
    # Set the shutdown event so the background task can stop gracefully.
    shutdown_event: Event = info['shutdown_event']
    shutdown_event.set()

    # Wait for the background task to finish.
    time_ticker_task: asyncio.Task = info['time_ticker_task']
    await time_ticker_task
```

First we retrieve the event from the application's info and set it. In the
background task the loop will exit when it next checks the event.

```python
while not shutdown_event.is_set():
        ...
```

Next we fetch the task from the applications info and `await` it. When the
next timeout occurs in the background task it will exit it's loop, and the
background task gracefully shuts down.

## The Program

Here is the full code.

I've added a request handler which returns the time stored by the background
task to demonstrate that the web server is still able to handle requests.

```python
import asyncio
from asyncio import Event
from datetime import datetime
import logging
import uvicorn

from bareasgi import Application, text_writer

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger('background_tasks')

async def time_ticker(info, shutdown_event):
    LOGGER.debug('Starting the time ticker')

    while not shutdown_event.is_set():
        # Store the time
        info['now'] = datetime.now()
        LOGGER.debug('time: %s', info['now'])
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=1)
        except asyncio.TimeoutError:
            LOGGER.debug(
                'Timeout - normal behaviour when waiting with a timeout')
        except:
            LOGGER.exception('Failure - we should not see this exception')

    LOGGER.debug('The time ticker has stopped')

async def time_ticker_startup_handler(scope, info, request):
    # Create an event that can be set when the background task should shutdown.
    shutdown_event = Event()
    info['shutdown_event'] = shutdown_event

    # Create the background task.
    info['time_ticker_task'] = asyncio.create_task(
        time_ticker(info, shutdown_event)
    )

async def time_ticker_shutdown_handler(scope, info, request):
    # Set the shutdown event so the background task can stop gracefully.
    shutdown_event: Event = info['shutdown_event']
    LOGGER.debug('Stopping the time_ticker')
    shutdown_event.set()

    # Wait for the background task to finish.
    time_ticker_task: asyncio.Task = info['time_ticker_task']
    LOGGER.debug('Waiting for time_ticker')
    await time_ticker_task
    LOGGER.debug('time_ticker shutdown')


async def http_request_callback(scope, info, matches, content):
    headers = [
        (b'content-type', b'text/plain')
    ]
    return 200, headers, text_writer(f"Last time tick: {info.get('now')}")

app = Application(
    startup_handlers=[time_ticker_startup_handler],
    shutdown_handlers=[time_ticker_shutdown_handler]
)
app.http_router.add({'GET'}, '/{rest:path}', http_request_callback)

uvicorn.run(app, port=9009)
```

## Canceling

Rather than using an event we could have just cancelled the task.

```python
async def time_ticker_shutdown_handler(scope, info, request):
    time_ticker_task: asyncio.Task = info['time_ticker_task']
    try:
        time_ticker_task.cancel()
        await time_ticker_task
    except asyncio.CancellationError:
        pass
```

The background task might then look as follows.

```python
async def time_ticker(info, shutdown_event):
    while True:
        # Store the time
        info['now'] = datetime.now()
        print(f"time: {info['now']}")
        try:
            await asyncio.sleep(1)
        except asyncio.CancellationError:
            return # Catch the task.cancel() and exit
        except:
            print('Failure - we should not see this exception')

    print('The time ticker has stopped')
```

## Cancel or Shutdown Event?

In the above example cancelling the task would have been appropriate. Nothing
bad would happen, and no data would be lost.

The event approach is useful where cancelling the task would result in some
kind of corrupt state. For example if a database write was in progress, or
a message queue was being serviced.

## Gotcha!

If we had a large program running many background tasks with multiple startup
handlers, it would seem reasonable to create the shutdown event right at the
start.

```python
# This won't work!
app = Application(info={'shutdown_event': asyncio.Event()})
```

Unfortunately this won't work and will lead to hours of frustration.

When an ASGI server starts it creates a **new** event loop. However the
`asyncio.Event()` call attached the event to the existing event loop. At the
point the event is awaited you will get an error telling you the coroutine was
attached to another event loop, which is true, but not helpful!

This is true for anything that can be awaited. They must all be created in the
context of the ASGI server's event loop.

## What next?

Either go back to the [table of contents](index.md) or go
to the [https](https.md) tutorial.

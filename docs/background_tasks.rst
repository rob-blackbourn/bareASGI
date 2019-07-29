Background Tasks
================

It is a common requirement to run background tasks while the server is processing
requests. For example incomming data might have to be processed before being used
in subsequent responses.

An important implementation details is that any code which uses the asyncio event
loop (e.g. asyncio.Event(), asyncio.Queue(), etc.) *must* be done in the context
of the ASGI server. Failure to do this will lead to errors complaining that the
object is owned by a different event loop.

This can be achieved by passing the application startup and shutdown handlers:

.. code-block:: python

    async def my_startup_handler(scope: Scope, info: Info, request: Message) -> None:
        ...

    async def my_shutdown_handler(scope: Scope, info: Info, request: Message) -> None:
        ...

    # Create the application with startup and shutdown handlers.
    app = Application(
        startup_handlers=[my_startup_handler],
        shutdown_handlers=[my_shutdown_handler]
    )

The tasks may be one-off or long running. The long-running tasks can be gracefully terminated
with shutdown handlers.

Here is an example of a long running task which simply ticks every second.

.. code-block:: python

    async def time_ticker(shutdown_event: Event) -> None:

        while not shutdown_event.is_set():
            log.debug(f'time: {datetime.now()}')
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=1)
            except asyncio.TimeoutError:
                log.debug('Timeout - normal behaviour when waiting with a timeout')
            except:
                log.exception('Failure - we should not see this exception')

        log.debug('The time ticker has stopped')

    async def time_ticker_startup_handler(scope: Scope, info: Info, request: Message) -> None:
        # Create an event that can be set when the background task should shutdown.
        shutdown_event = Event()
        info['shutdown_event'] = shutdown_event

        # Create the background task.
        info['time_ticker_task'] = asyncio.create_task(time_ticker(shutdown_event))

    async def time_ticker_shutdown_handler(scope: Scope, info: Info, request: Message) -> None:
        # Set the shutdown event so the background task can stop gracefully.
        shutdown_event: Event = info['shutdown_event']
        log.debug('Stopping the time_ticker')
        shutdown_event.set()

        # Wait for the background task to finish.
        time_ticker_task: asyncio.Task = info['time_ticker_task']
        log.debug('Waiting for time_ticker')
        await time_ticker_task
        log.debug('time_ticker shutdown')

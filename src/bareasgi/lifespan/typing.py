"""Lifespan Protocol

Version: 2.0 (2019-03-20)

The Lifespan ASGI sub-specification outlines how to communicate lifespan events
such as startup and shutdown within ASGI. This refers to the lifespan of the
main event loop. In a multi-process environment there will be lifespan events in
each process.

The lifespan messages allow for an application to initialise and shutdown in the
context of a running event loop. An example of this would be creating a
connection pool and subsequently closing the connection pool to release the
connections.

A possible implementation of this protocol is given below:

```python
async def app(scope, receive, send):
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                ... # Do some startup here!
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                ... # Do some shutdown here!
                await send({'type': 'lifespan.shutdown.complete'})
                return
    else:
        pass # Handle other types
```
"""

from typing import Awaitable, Callable, Literal, TypedDict, Union

from ..versions import ASGIVersions


class LifespanScope(TypedDict):
    """Scope

    The lifespan scope exists for the duration of the event loop.

    The scope information passed in scope contains basic metadata:

    Attributes:
        type (Literal["lifespan"]): The message type.
        asgi (ASGIVersions): The version of the ASGI spec.

    Notes:
        If an exception is raised when calling the application callable with a
        lifespan.startup message or a scope with type lifespan, the server must
        continue but not send any lifespan events.

        This allows for compatibility with applications that do not support the
        lifespan protocol. If you want to log an error that occurs during
        lifespan startup and prevent the server from starting, then send back
        `lifespan.startup.failed` instead.


    """
    type: Literal["lifespan"]
    asgi: ASGIVersions


class LifespanStartupEvent(TypedDict):
    """Startup - `receive` event

    Sent to the application when the server is ready to startup and receive
    connections, but before it has started to do so.

    Attributes:

        type (Literal["lifespan.startup"]): The message type.
    """
    type: Literal["lifespan.startup"]


class LifespanShutdownEvent(TypedDict):
    """Shutdown - `receive` event

    Sent to the application when the server has stopped accepting connections
    and closed all active connections.

    Attributes:
        type (Literal["lifespan.shutdown"]): The message type.
    """
    type: Literal["lifespan.shutdown"]


class LifespanStartupCompleteEvent(TypedDict):
    """Startup Complete - `send` event

    Sent by the application when it has completed its startup. A server must
    wait for this message before it starts processing connections.

    Attributes:

        type (Literal["lifespan.startup.complete"]): The message type.
    """
    type: Literal["lifespan.startup.complete"]


class LifespanStartupFailedEvent(TypedDict):
    """Startup Failed - `send` event

    Sent by the application when it has failed to complete its startup. If a
    server sees this it should log/print the message provided and then exit.

    Attributes:

        type (Literal["lifespan.startup.failed"]): The message type.
        message (str) – Optional; if missing defaults to `""`.
    """
    type: Literal["lifespan.startup.failed"]
    message: str


class LifespanShutdownCompleteEvent(TypedDict):
    """Shutdown Complete - `send` event

    Sent by the application when it has completed its cleanup. A server must
    wait for this message before terminating.

    Attributes:
        type (Literal["lifespan.shutdown.complete"]): The message type.
    """
    type: Literal["lifespan.shutdown.complete"]


class LifespanShutdownFailedEvent(TypedDict):
    """Shutdown Failed - `send` event

    Sent by the application when it has failed to complete its cleanup. If a
    server sees this it should log/print the message provided and then
    terminate.

    Attributes:

        type (Literal["lifespan.shutdown.failed"]): `"lifespan.shutdown.failed"`.
        message (str): Optional; if missing defaults to `""`.
    """
    type: Literal["lifespan.shutdown.failed"]
    message: str


type ASGILifespanReceiveEventType = Union[
    Literal["lifespan.startup"],
    Literal["lifespan.shutdown"]
]

type ASGILifespanReceiveEvent = Union[
    LifespanStartupEvent,
    LifespanShutdownEvent,
]

type ASGILifespanSendEventType = Union[
    Literal["lifespan.startup.complete"],
    Literal["lifespan.startup.failed"],
    Literal["lifespan.shutdown.complete"],
    Literal["lifespan.shutdown.failed"]
]

type ASGILifespanSendEvent = Union[
    LifespanStartupCompleteEvent,
    LifespanStartupFailedEvent,
    LifespanShutdownCompleteEvent,
    LifespanShutdownFailedEvent,
]

type ASGILifespanReceiveCallable = Callable[
    [],
    Awaitable[ASGILifespanReceiveEvent]
]
type ASGILifespanSendCallable = Callable[
    [ASGILifespanSendEvent],
    Awaitable[None]
]

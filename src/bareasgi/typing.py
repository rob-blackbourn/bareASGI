"""ASGI Application"""

from typing import Awaitable, Callable, Protocol, Union

from .http.typing import (
    HTTPScope,
    HTTPRequestEvent,
    HTTPDisconnectEvent,
    HTTPResponseStartEvent,
    HTTPResponseBodyEvent,
    HTTPServerPushEvent
)

from .websockets.typing import (
    WebSocketScope,
    WebSocketConnectEvent,
    WebSocketReceiveEvent,
    WebSocketDisconnectEvent,
    WebSocketAcceptEvent,
    WebSocketSendEvent,
    WebSocketResponseStartEvent,
    WebSocketResponseBodyEvent,
    WebSocketCloseEvent
)

from .lifespan.typing import (
    LifespanScope,
    LifespanStartupEvent,
    LifespanShutdownEvent,
    LifespanStartupCompleteEvent,
    LifespanStartupFailedEvent,
    LifespanShutdownCompleteEvent,
    LifespanShutdownFailedEvent
)

type WWWScope = HTTPScope | WebSocketScope
type Scope = HTTPScope | WebSocketScope | LifespanScope

type ASGIReceiveEvent = Union[
    HTTPRequestEvent,
    HTTPDisconnectEvent,
    WebSocketConnectEvent,
    WebSocketReceiveEvent,
    WebSocketDisconnectEvent,
    LifespanStartupEvent,
    LifespanShutdownEvent,
]


type ASGISendEvent = Union[
    HTTPResponseStartEvent,
    HTTPResponseBodyEvent,
    HTTPServerPushEvent,
    HTTPDisconnectEvent,
    WebSocketAcceptEvent,
    WebSocketSendEvent,
    WebSocketResponseStartEvent,
    WebSocketResponseBodyEvent,
    WebSocketCloseEvent,
    LifespanStartupCompleteEvent,
    LifespanStartupFailedEvent,
    LifespanShutdownCompleteEvent,
    LifespanShutdownFailedEvent,
]

type ASGIReceiveCallable = Callable[[], Awaitable[ASGIReceiveEvent]]
type ASGISendCallable = Callable[[ASGISendEvent], Awaitable[None]]


class ASGI2Protocol(Protocol):
    """Protocol for ASGIv2"""

    def __init__(self, scope: Scope) -> None:
        ...

    async def __call__(
        self, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        ...


type ASGI2Application = type[ASGI2Protocol]
type ASGI3Application = Callable[
    [
        Scope,
        ASGIReceiveCallable,
        ASGISendCallable,
    ],
    Awaitable[None],
]
type ASGIApplication = ASGI2Application | ASGI3Application

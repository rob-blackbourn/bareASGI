from typing import Mapping, AsyncIterable, AsyncGenerator
from typing import Any, Callable, Optional, Tuple, List
from typing import Awaitable

Scope = Mapping[str, Any]
Message = Mapping[str, Any]
Context = Optional[Mapping[str, Any]]
Info = Optional[Mapping[str, Any]]

Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]

ASGIInstance = Callable[[Receive, Send], Awaitable[None]]
ASGIApp = Callable[[Scope], ASGIInstance]

StartupHandler = Callable[[], Awaitable[None]]
ShutdownHandler = Callable[[], Awaitable[None]]
LifespanHandler = Callable[[Scope, Info, Message], Awaitable[None]]

Header = Tuple[bytes, bytes]
Headers = List[Header]

RouteMatches = Mapping[str, Any]
Content = AsyncIterable[bytes]
Reply = Callable[[int, List[Header], AsyncGenerator[bytes, None]], Awaitable[None]]

WebHandler = Callable[[Scope, RouteMatches, Content, Reply], Awaitable[None]]
RouteHandler = Callable[[Scope], Tuple[WebHandler, Mapping[str, Any]]]

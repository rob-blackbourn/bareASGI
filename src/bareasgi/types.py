from abc import ABCMeta, abstractmethod
from typing import Mapping, AsyncIterable, AsyncGenerator, Union, AbstractSet
from typing import Any, Callable, Optional, Tuple, List
from typing import Awaitable


class ParseError(Exception):
    pass


class HttpInternalError(Exception):
    pass


class HttpDisconnectError(Exception):
    pass


class WebSocketInternalError(Exception):
    pass


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
Reply = Callable[[int, List[Header], Optional[AsyncGenerator[bytes, None]]], Optional[Awaitable[None]]]


class WebSocket(metaclass=ABCMeta):

    @abstractmethod
    async def accept(self, subprotocol: Optional[str] = None) -> None:
        raise NotImplementedError


    @abstractmethod
    async def receive(self) -> Optional[Union[bytes, str]]:
        raise NotImplementedError


    @abstractmethod
    async def send(self, content: Union[bytes, str]) -> None:
        raise NotImplementedError


    @abstractmethod
    async def close(self, code: int = 1000) -> None:
        raise NotImplementedError


HttpResponse = Tuple[int, Optional[List[Header]], Optional[AsyncGenerator[bytes, None]]]
HttpRequestCallback = Callable[[Scope, Info, RouteMatches, Content], Awaitable[HttpResponse]]
WebSocketRequestCallback = Callable[[Scope, Info, RouteMatches, WebSocket], Awaitable[None]]
HttpMiddlewareCallback = Callable[[Scope, Info, RouteMatches, Content, HttpRequestCallback], Awaitable[HttpResponse]]


class HttpRouter(metaclass=ABCMeta):

    @property
    @abstractmethod
    def not_found_response(self):
        raise NotImplementedError


    @not_found_response.setter
    @abstractmethod
    def not_found_response(self, value: HttpResponse):
        raise NotImplementedError


    @abstractmethod
    def add(self, methods: AbstractSet[str], path: str, callback: HttpRequestCallback) -> None:
        raise NotImplementedError


    @abstractmethod
    def __call__(self, scope: Scope) -> Tuple[Optional[HttpRequestCallback], Optional[RouteMatches]]:
        raise NotImplementedError


class WebSocketRouter(metaclass=ABCMeta):

    @abstractmethod
    def add(self, path: str, callback: WebSocketRequestCallback) -> None:
        raise NotImplementedError


    @abstractmethod
    def __call__(self, scope: Scope) -> Tuple[Optional[WebSocketRequestCallback], Optional[RouteMatches]]:
        raise NotImplementedError

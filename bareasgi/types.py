"""Types for bareASGI and bareClient"""

from abc import ABCMeta, abstractmethod
from typing import (
    AbstractSet,
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    Union
)

from bareutils import header


Scope = Dict[str, Any]

Receive = Callable[[], Awaitable[Dict[str, Any]]]
Send = Callable[[Dict[str, Any]], Awaitable[None]]

ASGIInstance = Callable[[Receive, Send], Awaitable[None]]
ASGIApp = Callable[[Scope], ASGIInstance]





PushResponse = Tuple[str, List[Tuple[bytes, bytes]]]
PushResponses = Iterable[PushResponse]


class WebSocket(metaclass=ABCMeta):
    """The interface for a server side WebSocket."""

    @abstractmethod
    async def accept(
            self,
            subprotocol: Optional[str] = None,
            headers: Optional[List[Tuple[bytes, bytes]]] = None
    ) -> None:
        """Accept the socket.

        This must be done before any other action is taken.

        Args:
            subprotocol (Optional[str], optional): An optional subprotocol sent
                by the client. Defaults to None.
            headers (Optional[List[Tuple[bytes, bytes]]], optional): Optional
                headers to send. Defaults to None.
        """

    @abstractmethod
    async def receive(self) -> Optional[Union[bytes, str]]:
        """Receive data from the WebSocket.

        Returns:
            Optional[Union[bytes, str]]: Either bytes of a string depending on
                the client.
        """

    @abstractmethod
    async def send(self, content: Union[bytes, str]) -> None:
        """Send data to the client.

        Args:
            content (Union[bytes, str]): Either bytes or a string.
        """

    @abstractmethod
    async def close(self, code: int = 1000) -> None:
        """Close the WebSocket.

        Args:
            code (int, optional): The reason code. Defaults to 1000.
        """


class HttpRequest:

    def __init__(
            self,
            scope: Scope,
            info: Dict[str, Any],
            context: Dict[str, Any],
            matches: Mapping[str, Any],
            body: AsyncIterable[bytes]
    ) -> None:
        self.scope = scope
        self.info = info
        self.context = context
        self.matches = matches
        self.body = body

    @property
    def url(self) -> str:
        """Make the url from the scope"""
        scheme = self.scope['scheme']
        host = header.find(b'host', self.scope['headers'], b'unknown')
        assert host is not None
        path = self.scope['path']
        return f"{scheme}://{host.decode()}{path}"


class HttpResponse:

    def __init__(
            self,
            status: int,
            headers: Optional[List[Tuple[bytes, bytes]]] = None,
            body: Optional[AsyncIterable[bytes]] = None,
            pushes: Optional[PushResponses] = None
    ) -> None:
        self.status = status
        self.headers = headers
        self.body = body
        self.pushes = pushes


class WebSocketRequest:

    def __init__(
            self,
            scope: Scope,
            info: Dict[str, Any],
            matches: Mapping[str, Any],
            web_socket: WebSocket
    ) -> None:
        self.scope = scope
        self.info = info
        self.matches = matches
        self.web_socket = web_socket


HttpRequestCallback = Callable[
    [HttpRequest],
    Awaitable[HttpResponse]
]
WebSocketRequestCallback = Callable[
    [WebSocketRequest],
    Awaitable[None]
]
HttpChainedCallback = Callable[
    [HttpRequest],
    Awaitable[HttpResponse]
]
HttpMiddlewareCallback = Callable[
    [HttpRequest, HttpChainedCallback],
    Awaitable[HttpResponse]
]


class HttpRouter(metaclass=ABCMeta):
    """The interface for an HTTP router"""

    @property  # type: ignore
    @abstractmethod
    def not_found_response(self) -> HttpResponse:
        """The response when a handler could not be found for a method/path

        Returns:
            HttpResponse: The response when a route cannot be found.
        """

    @not_found_response.setter  # type: ignore
    @abstractmethod
    def not_found_response(self, value: HttpResponse) -> None:
        ...

    @abstractmethod
    def add(
            self,
            methods: AbstractSet[str],
            path: str,
            callback: HttpRequestCallback
    ) -> None:
        """Add an HTTP request handler

        Args:
            methods (AbstractSet[str]): The supported HTTP methods.
            path (str): The path.
            callback (HttpRequestCallback): The request handler.
        """

    @abstractmethod
    def resolve(
            self,
            method: str,
            path: str
    ) -> Tuple[HttpRequestCallback, Mapping[str, Any]]:
        """Resolve a request to a handler with the route matches

        Args:
            method (str): The HTTP method.
            path (str): The path.

        Returns:
            Tuple[HttpRequestCallback, Mapping[str, Any]]: A handler and the route
                matches.
        """


class WebSocketRouter(metaclass=ABCMeta):
    """The interface for a WebSocket router"""

    @abstractmethod
    def add(
            self,
            path: str,
            callback: WebSocketRequestCallback
    ) -> None:
        """Add the WebSocket handler for a route

        Args:
            path (str): The path.
            callback (WebSocketRequestCallback): The handler
        """

    @abstractmethod
    def resolve(
            self,
            path: str
    ) -> Tuple[WebSocketRequestCallback, Mapping[str, Any]]:
        """Resolve a route to a handler

        Args:
            path (str): The path

        Returns:
            Tuple[WebSocketRequestCallback, Mapping[str, Any]]: A handler and the
                route matches
        """

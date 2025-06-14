"""Websocket"""

from typing import Awaitable, Callable, Iterable, Union

from typing import Literal, TypedDict

from ..versions import ASGIVersions


class WebSocketScope(TypedDict):
    """Websocket Connection Scope

    WebSocket connections’ scope lives as long as the socket itself - if the
    application dies the socket should be closed, and vice-versa.

    The connection scope information passed in scope contains initial connection
    metadata (mostly from the HTTP request line and headers):

    Attributes:
        type (Literal["websocket"]): The message type.
        asgi (ASGIVersions): The version of the ASGI spec.
        http_version (str): One of `"1.1"` or `"2"`. Optional; if missing
            default is `"1.1"`.
        scheme (str): URL scheme portion (likely `"ws"` or `"wss"`). Optional
            (but must not be empty); default is `"ws"`.
        path (str): HTTP request target excluding any query string, with
            percent-encoded sequences and UTF-8 byte sequences decoded into
            characters.
        raw_path (bytes): The original HTTP path component unmodified from the
            bytes that were received by the web server. Some web server
            implementations may be unable to provide this. Optional; if missing
            defaults to `None`.
        query_string (bytes): URL portion after the ?. Optional; if missing
            default is empty string.
        root_path (str) – The root path this application is mounted at; same as
            `SCRIPT_NAME` in WSGI. Optional; if missing defaults to empty
            string.
        headers (Iterable[tuple[bytes, bytes]]): An iterable of `[name, value]`
            two-item iterables, where name is the header name and value is the
            header value. Order should be preserved from the original HTTP
            request; duplicates are possible and must be preserved in the
            message as received. Header names must be lowercased. Pseudo headers
            (present in HTTP/2 and HTTP/3) must be removed; if `:authority` is
            present its value must be added to the start of the iterable with
            host as the header name or replace any existing host header already
            present.
        client (Optional[Tuple[str, int]]): A two-item iterable of
            `[host, port]`, where host is the remote host’s IPv4 or IPv6
            address, and port is the remote port. Optional; if missing defaults
            to `None`.
        server (Optional[Tuple[str, Optional[int]]]): Either a two-item iterable
            of `[host, port]`, where host is the listening address for this
            server, and port is the integer listening port, or `[path, None]`
            where path is that of the unix socket. Optional; if missing defaults
            to `None`.
        subprotocols (Iterable[str]): Subprotocols the client advertised.
            Optional; if missing defaults to empty list.    
    """
    type: Literal["websocket"]
    asgi: ASGIVersions
    http_version: str
    scheme: str
    path: str
    raw_path: bytes
    query_string: bytes
    root_path: str
    headers: Iterable[tuple[bytes, bytes]]
    client: tuple[str, int] | None
    server: tuple[str, int | None] | None
    subprotocols: Iterable[str]
    extensions: dict[str, dict[object, object]] | None


class WebSocketConnectEvent(TypedDict):
    """Connect - `receive` event

    Sent to the application when the client initially opens a connection and
    is about to finish the WebSocket handshake.

    This message must be responded to with either an `Accept` message or a
    `Close` message before the socket will pass `websocket.receive` messages.
    The protocol server must send this message during the handshake phase of the
    WebSocket and not complete the handshake until it gets a reply, returning
    HTTP status code `403` if the connection is denied.

    Attributes:
        type (Literal["websocket.connect"]): The message type.
    """
    type: Literal["websocket.connect"]


class WebSocketAcceptEvent(TypedDict):
    """Accept - `send` event

    Sent by the application when it wishes to accept an incoming connection.

    Attributes:
        type (Literal["websocket.accept"]): The message type.
        subprotocol (str): The subprotocol the server wishes to accept.
        Optional; if missing defaults to `None`.
        headers (Iterable[tuple[bytes, bytes]]) – An iterable of `[name, value]`
            two-item iterables, where name is the header name, and value is the
            header value. Order must be preserved in the HTTP response. Header
            names must be lowercased. Must not include a header named
            `sec-websocket-protocol`; use the subprotocol key instead. Optional;
            if missing defaults to an empty list. Added in spec version 2.1.
            Pseudo headers (present in HTTP/2 and HTTP/3) must not be present.
    """
    type: Literal["websocket.accept"]
    subprotocol: str | None
    headers: Iterable[tuple[bytes, bytes]]


class WebSocketReceiveEvent(TypedDict):
    """Receive - `receive` event

    Sent to the application when a data message is received from the client.

    Attributes:
        type (Literal["websocket.receive"]): The message type.
        bytes (bytes | None): The message content, if it was binary mode, or
            `None`. Optional; if missing, it is equivalent to `None`.
        text (str | None): The message content, if it was text mode, or
            `None`. Optional; if missing, it is equivalent to `None`.

    Notes:
        Exactly one of bytes or text must be non-None. One or both keys may be
        present, however.
    """
    type: Literal["websocket.receive"]
    bytes: bytes | None
    text: str | None


class WebSocketSendEvent(TypedDict):
    """Send - `send` event

    Sent by the application to send a data message to the client.

    Attributes:

        type (Literal["websocket.send"]): The message type.
        bytes (bytes | None): Binary message content, or `None`. Optional; if
            missing, it is equivalent to `None`.
        text (str | None): Text message content, or `None`. Optional; if
            missing, it is equivalent to `None`.

    Notes:
        Exactly one of bytes or text must be non-None. One or both keys may be
        present, however.
    """
    type: Literal["websocket.send"]
    bytes: bytes | None
    text: str | None


class WebSocketResponseStartEvent(TypedDict):
    type: Literal["websocket.http.response.start"]
    status: int
    headers: Iterable[tuple[bytes, bytes]]


class WebSocketResponseBodyEvent(TypedDict):
    type: Literal["websocket.http.response.body"]
    body: bytes
    more_body: bool


class WebSocketDisconnectEvent(TypedDict):
    """Disconnect - `receive` event

    Sent to the application when either connection to the client is lost, either
    from the client closing the connection, the server closing the connection,
    or loss of the socket.

    Attributes:
        type (Literal["websocket.disconnect"]): The message type.
        code (int): The WebSocket close code, as per the WebSocket spec.
    """
    type: Literal["websocket.disconnect"]
    code: int


class WebSocketCloseEvent(TypedDict):
    """Close - `send` event

    Sent by the application to tell the server to close the connection.

    If this is sent before the socket is accepted, the server must close the
    connection with a HTTP 403 error code (Forbidden), and not complete the
    WebSocket handshake; this may present on some browsers as a different
    WebSocket error code (such as 1006, Abnormal Closure).

    If this is sent after the socket is accepted, the server must close the
    socket with the close code passed in the message (or `1000` if none is
    specified).

    Attributes:
        type (Literal["websocket.close"]): The message type.
        code (int): The WebSocket close code, as per the WebSocket spec.
            Optional; if missing defaults to `1000`.
    """
    type: Literal["websocket.close"]
    code: int


type ASGIWebSocketReceiveEventType = Union[
    Literal["websocket.connect"],
    Literal["websocket.receive"],
    Literal["websocket.disconnect"]
]

type ASGIWebSocketReceiveEvent = Union[
    WebSocketConnectEvent,
    WebSocketReceiveEvent,
    WebSocketDisconnectEvent,
]

type ASGIWebSocketSendEventType = Union[
    Literal["websocket.accept"],
    Literal["websocket.send"],
    Literal["websocket.close"]
]

type ASGIWebSocketSendEvent = Union[
    WebSocketAcceptEvent,
    WebSocketSendEvent,
    WebSocketCloseEvent,
]

type ASGIWebSocketReceiveCallable = Callable[
    [],
    Awaitable[ASGIWebSocketReceiveEvent]
]
type ASGIWebSocketSendCallable = Callable[
    [ASGIWebSocketSendEvent],
    Awaitable[None]
]

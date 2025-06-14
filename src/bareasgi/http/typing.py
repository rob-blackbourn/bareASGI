"""HTTP

The HTTP format covers HTTP/1.0, HTTP/1.1 and HTTP/2, as the changes in HTTP/2
are largely on the transport level. A protocol server should give different
scopes to different requests on the same HTTP/2 connection, and correctly
multiplex the responses back to the same stream in which they came. The HTTP
version is available as a string in the scope.

Multiple header fields with the same name are complex in HTTP. RFC 7230 states
that for any header field that can appear multiple times, it is exactly
equivalent to sending that header field only once with all the values joined
by commas.

However, RFC 7230 and RFC 6265 make it clear that this rule does not apply to
the various headers used by HTTP cookies (`Cookie` and `Set-Cookie`). The
`Cookie` header must only be sent once by a user-agent, but the `Set-Cookie`
header may appear repeatedly and cannot be joined by commas. The ASGI design
decision is to transport both request and response headers as lists of 2-element
'[name, value]' lists and preserve headers exactly as they were provided.

The HTTP protocol should be signified to ASGI applications with a `type` value
of 'http'.
"""

from typing import Any, Awaitable, Callable, Iterable, Literal, TypedDict, Union

from ..versions import ASGIVersions


class HTTPScope(TypedDict):
    """HTTP Connection Scope

    HTTP connections have a single-request connection scope - that is, your
    application will be called at the start of the request, and will last until
    the end of that specific request, even if the underlying socket is still
    open and serving multiple requests.

    If you hold a response open for long-polling or similar, the connection
    scope will persist until the response closes from either the client or
    server side.

    Attributes:
        type (Literal['http']): The message type.
        asgi (ASGIVersion): Version of the ASGI spec.
        asgi (Union[Literal['2.0', Literal['2.1']]]): Version of the ASGI HTTP
            spec this server understands; one of "2.0" or "2.1". Optional; if
            missing assume 2.0.
        http_version (str): One of "1.0", "1.1" or "2".
        method (str): The HTTP method name, uppercased.
        scheme (str): URL scheme portion (likely "http" or "https"). Optional
            (but must not be empty); default is "http".
        path (str): HTTP request target excluding any query string, with
            percent-encoded sequences and UTF-8 byte sequences decoded into
            characters.
        raw_path (bytes): The original HTTP path component unmodified from the
            bytes that were received by the web server. Some web server
            implementations may be unable to provide this. Optional; if missing
            defaults to None.
        query_string (bytes): URL portion after the ?, percent-encoded.
        root_path (str): The root path this application is mounted at; same as
            SCRIPT_NAME in WSGI. Optional; if missing defaults to "".
        headers (Iterable[tuple[byte string, byte string]]): An iterable of
            [name, value] two-item iterables, where name is the header name,
            and value is the header value. Order of header values must be
            preserved from the original HTTP request; order of header names is
            not important. Duplicates are possible and must be preserved in the
            message as received. Header names must be lowercased. Pseudo headers
            (present in HTTP/2 and HTTP/3) must be removed; if :authority
            is present its value must be added to the start of the iterable with
            host as the header name or replace any existing host header already
            present.
        client (Optional[tuple[str, int]]): A two-item iterable of [host, port],
            where host is the remote host’s IPv4 or IPv6 address, and port is
            the remote port as an integer. Optional; if missing defaults to None.
        server (Optional[tuple[str, Optional[int]]]): Either a two-item iterable
            of [host, port], where host is the listening address for this
            server, and port is the integer listening port, or [path, None]
            where path is that of the unix socket. Optional; if missing defaults
            to None.
        state (Optional[dict[str, Any]]): A copy of the namespace passed into the
            lifespan corresponding to this request. 
        extensions (Optional[dict[str, dict[object, object]]]): Optional server
            specific extensions.

    Notes:
        Servers are responsible for handling inbound and outbound chunked
        transfer encodings. A request with a chunked encoded body should be
        automatically de-chunked by the server and presented to the application
        as plain body bytes; a response that is given to the server with no
        `Content-Length` may be chunked as the server sees fit.
    """
    type: Literal['http']
    asgi: ASGIVersions
    http_version: str
    method: str
    scheme: str
    path: str
    raw_path: bytes
    query_string: bytes
    root_path: str
    headers: Iterable[tuple[bytes, bytes]]
    client: tuple[str, int] | None
    server: tuple[str, int | None] | None
    state: dict[str, Any] | None
    extensions: dict[str, dict[Any, Any]] | None


class HTTPRequestEvent(TypedDict):
    """Request - `receive` event

    Sent to the application to indicate an incoming request. Most of the
    request information is in the connection scope; the body message serves as a
    way to stream large incoming HTTP bodies in chunks, and as a trigger to
    actually run request code (as you should not trigger on a connection opening
    alone).

    Note that if the request is being sent using `Transfer-Encoding: chunked`,
    the server is responsible for handling this encoding. The `http.request`
    messages should contain just the decoded contents of each chunk.

    Attributes:
        type (Literal["http.request"]): The mesage type.
        body (bytes): Body of the request. Optional; if missing defaults to b"".
            If `more_body` is set, treat as start of body and concatenate on
            further chunks.
        more_body (bool): Signifies if there is additional content to come (as
            part of a Request message). If True, the consuming application
            should wait until it gets a chunk with this set to False. If False,
            the request is complete and should be processed. Optional; if
            missing defaults to False.
    """
    type: Literal["http.request"]
    body: bytes
    more_body: bool


class HTTPResponseStartEvent(TypedDict):
    """Response Start - `send` event

    Sent by the application to start sending a response to the client. Needs
    to be followed by at least one response content message. The protocol server
    must not start sending the response to the client until it has received at
    least one Response Body event.

    You may send a `Transfer-Encoding` header in this message, but the server
    must ignore it. Servers handle `Transfer-Encoding` themselves, and may opt
    to use `Transfer-Encoding: chunked` if the application presents a response
    that has no `Content-Length` set.

    Note that this is not the same as `Content-Encoding`, which the application
    still controls, and which is the appropriate place to set `gzip` or other
    compression flags.

    type (Literal["http.response.start"]): The message type.
    status (int): HTTP status code.
    headers (Iterable[tuple[bytes, bytes]]): An iterable of [name, value]
        two-item iterables, where name is the header name, and value is the
        header value. Order must be preserved in the HTTP response. Header names
        must be lowercased. Optional; if missing defaults to an empty list.
        Pseudo headers (present in HTTP/2 and HTTP/3) must not be present.
    """
    type: Literal["http.response.start"]
    status: int
    headers: Iterable[tuple[bytes, bytes]]


class HTTPResponseBodyEvent(TypedDict):
    """Response Body - `send` event

    Continues sending a response to the client. Protocol servers must flush any
    data passed to them into the send buffer before returning from a send call.
    If `more_body` is set to False this will close the connection.

        type (Literal["http.response.body"]): The message type.
        body (bytes): HTTP body content. Concatenated onto any previous body
            values sent in this connection scope. Optional; if missing defaults
            to `b""`.
        more_body (bool): Signifies if there is additional content to come (as
            part of a Response Body message). If `False`, response will be taken
            as complete and closed, and any further messages on the channel will
            be ignored. Optional; if missing defaults to `False`.    
    """
    type: Literal["http.response.body"]
    body: bytes
    more_body: bool


class HTTPServerPushEvent(TypedDict):
    """HTTP/2 Server Push - `send` event.

    HTTP/2 allows for a server to push a resource to a client by sending a push
    promise. ASGI servers that implement this extension will provide
    `http.response.push` in the extensions part of the scope:

    ```python
"scope": {
    ...
    "extensions": {
        "http.response.push": {},
    },
}
    ```

    An ASGI framework can initiate a server push by sending a message with the
    following keys. This message can be sent at any time after the Response
    Start message but before the final Response Body message.

    Attributes:

    type (Literal["http.response.push"]): The message type.
    path (str): HTTP path from URL, with percent-encoded sequences and UTF-8
        byte sequences decoded into characters.
    headers (Iterable[tuple[bytes, bytes]]): An iterable of [name, value]
        two-item iterables, where name is the header name, and value is the
        header value. Header names must be lowercased. Pseudo headers (present
        in HTTP/2 and HTTP/3) must not be present.

    Notes:
        The ASGI server should then attempt to send a server push (or push
        promise) to the client. If the client supports server push, the server
        should create a new connection to a new instance of the application and
        treat it as if the client had made a request.

        The ASGI server should set the pseudo :authority header value to be the
        same value as the request that triggered the push promise.
    """

    type: Literal["http.response.push"]
    path: str
    headers: Iterable[tuple[bytes, bytes]]


class HTTPDisconnectEvent(TypedDict):
    """Disconnect - `receive` event

    Sent to the application when a HTTP connection is closed or if receive
    is called after a response has been sent. This is mainly useful for
    long-polling, where you may want to trigger cleanup code if the connection
    closes early.

    Attributes:
        type (Literal["http.disconnect"]): The message type.
    """
    type: Literal["http.disconnect"]


type ASGIHTTPReceiveEventType = Union[
    Literal["http.request"],
    Literal["http.disconnect"]
]

type ASGIHTTPReceiveEvent = Union[
    HTTPRequestEvent,
    HTTPDisconnectEvent
]

type ASGIHTTPSendEventType = Union[
    Literal["http.response.start"],
    Literal["http.response.body"],
    Literal["http.response.push"],
]

type ASGIHTTPSendEvent = Union[
    HTTPResponseStartEvent,
    HTTPResponseBodyEvent,
    HTTPServerPushEvent,
]

type ASGIHTTPReceiveCallable = Callable[[], Awaitable[ASGIHTTPReceiveEvent]]
type ASGIHTTPSendCallable = Callable[[ASGIHTTPSendEvent], Awaitable[None]]

# Web Sockets

The bareASGI framework has full support for 
[WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket).


You can find the ASGI documentation
[here](https://asgi.readthedocs.io/en/latest/specs/www.html#websocket).

The source code for the following example can be found
[here](../examples/web_socket_nt.py)
(and here [here](../examples/web_socket.py) with typing).

# The WebSocket Handler

The WebSocket request handler has a different prototype than the http request
handler.

Here's the handler from our example program.

```python
async def websocket_handler(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        web_socket: WebSocket
) -> None:
    """The websocket callback handler"""
    await web_socket.accept()

    try:
        while True:
            text = await web_socket.receive()
            if text is None:
                break
            await web_socket.send('You said: ' + text)
    except Exception as error:
        print(error)

    await web_socket.close()
```

As you can see the difference is the last parameter, the `web_socket` itself.

The first thing we need to do is accept the connection (assuming we want to).
Then we wait for a message to be sent from the client, 
`text = await web_socket.receive()`, then send it back,
`await web_socket.send('You said: ' + text)`.

## API

The `web_socket` is an object with the following prototype:

```python
class WebSocket:

    async def accept(self, subprotocol: Optional[str] = None, headers: Optional[List[Headers]] = None) -> None:
        """Accept the socket.

        This must be done before any other action is taken.

        :param subprotocol: An optional subprotocol sent by the client.
        :param headers: Optional headers sent by the client.
        """

    async def receive(self) -> Optional[Union[bytes, str]]:
        """Receive data from the WebSocket.

        :return: Either bytes of a string depending on the client.
        """

    async def send(self, content: Union[bytes, str]) -> None:
        """Send data to the client.

        :param content: Either bytes or a string.
        """

    async def close(self, code: int = 1000) -> None:
        """Closes the WebSocket.

        :param code: The reason code (defaults to 1000).
        """

    @property
    def code(self) -> Optional[int]:
        """The close code
        
        :return: The code returned when the WebSocket was closed otherwise None
        :rtype: Optional[int]
        """
```

## HTTP/2 and haproxy

There are some interesting issues around using HTTP/2 for WebSockets.

At the time of writing FireFox is the only browser that supports HTTP/2 and
WebSockets. Other browsers will downgrade the connection to HTTP/1.1.

This means that non-FireFox browsers with create a new connection for the
WebSocket, rather than use the existing connection as they would for an HTTP/2
session.

If the web server sits behind a proxy server (specifically haproxy), the proxy
server will only negotiate the protocol on the initial connect. This leads
to the subsequent downgrade being discarded, and the WebSocket connection fails.

If you have this setup, unless you can guarantee all your clients use FireFox,
you will have to clamp your haproxy to HTTP/1.1.

If you don't require the two way facility that WebSockets offer you can use
server sent events or a streaming.


## What next?

Either go back to the [table of contents](index.md) or go
to the [headers (including cookies)](headers.md) tutorial.

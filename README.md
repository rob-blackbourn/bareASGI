# bareasgi

A lightweight ASGI framework

## Status

Work in progress.

## Overview

This is a _bare_ ASGI web server framework. The goal is to provide
a minimal implementation, with other facilities (serving static files, CORS, sessions, etc.)
being implemented by optional packages. The goal is to keep the implementation
clear and lightweight.

## Functionality

The framework supports:
* Http,
* WebSockets,
* A basic method and path based router,
* Middleware. 

## Examples

These examples use [uvicorn](https://www.uvicorn.org/) as the ASGI server.

### Simple Client

Here is a simple example which returns some text.

```python
import uvicorn
from bareasgi import Application, text_writer

async def http_request_callback(scope, info, matches, content):
    return 200, [(b'content-type', b'text/plain')], text_writer('This is not a test')

app = Application()
app.http_router.add({'GET'}, '/{rest:path}', http_request_callback)

uvicorn.run(app, port=9009)
```

### Rest Server

Here is a simple rest server.

```python
import uvicorn
import json
from bareasgi import Application, text_reader, text_writer

async def get_info(scope, info, matches, content):
    text = json.dumps(info)
    return 200, [(b'content-type', b'application/json')], text_writer(text)

async def set_info(scope, info, matches, content):
    text = await text_reader(content)
    data = json.loads(text)
    info.update(data)
    return 204, None, None

app = Application(info={'name': 'Michael Caine'})
app.http_router.add({'GET'}, '/info', get_info)
app.http_router.add({'POST'}, '/info', set_info)

uvicorn.run(app, port=9009)
```

### WebSockets

A WebSocket example can be found in the examples folder. Here is the handler.

```python
async def test_callback(scope, info, matches, web_socket):
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

### Middleware

Here is a simple middleware example.

```python
import uvicorn
from bareasgi import Application, text_writer

async def first_middleware(scope, info, matches, content, handler):
    info['message'] = 'This is first the middleware. '
    response = await handler(scope, info, matches, content)
    return response


async def second_middleware(scope, info, matches, content, handler):
    info['message'] += 'This is the second middleware.'
    response = await handler(scope, info, matches, content)
    return response


async def http_request_callback(scope, info, matches, content):
    return 200, [(b'content-type', b'text/plain')], text_writer(info['message'])


app = Application(middlewares=[first_middleware, second_middleware])
app.http_router.add({'GET'}, '/test', http_request_callback)

uvicorn.run(app, port=9009)
```

## API

### Application

The application class has the following constructor:

```python
Application(
    middlewares: Optional[List[HttpMiddlewareCallback]],
    http_router: Optional[HttpRouter],
    web_socket_router: Optional[WebSocketRouter],
    startup_handlers: Optional[List[StartupHandler]],
    shutdown_handlers: Optional[List[ShutdownHandler]],
    not_found_response: Optional[HttpResponse],
    info: Optional[MutableMapping[str, Any]])
```

All arguments are optional.

The `info` argument provides a place for application specific data.

The application provides some properties that ccan be used for configuration:

```python
Application.info -> MutableMapping[str, Any]
Application.middlewares -> List[]
Application.http_router -> HttpRouter
Application.ws_router-> WebSocketRouter
Application.startup_handlers -> List[StartupHandler]
Application.shutdown_handlers -> List[ShutdownHandler]
```

### Routers

The routers are split into two: HTTP and WebSockets.

#### HttpRouter

The http router has the following structure:

```python
class HttpRouter:

    @property
    def not_found_response(self):
        ...

    @not_found_response.setter
    def not_found_response(self, value: HttpResponse):
        ...

    def add(self, methods: AbstractSet[str], path: str, callback: HttpRequestCallback) -> None:
        ...
```

### WebSocketRouter

The WebSocket router has the following structure:

```python
class WebSocketRouter(metaclass=ABCMeta):

    def add(self, path: str, callback: WebSocketRequestCallback) -> None:
        ...
```

### Paths

Here are some eexample paths:

```python
literal_path = '/foo/bar'
capture_trailing_paths = '/foo/{path}'
variables_path = '/foo/{name}/{id:int}/{created:datetime:%Y-%m-%d}'
```

Captured path segments are passed in to the callbacks as a dicctionary of route matches.

## Callacks

The framework uses async callbacks to handle requests.

### HttpRequestCallback

The HTTP request callback has the following structure:

```python
async def http_request_callback(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    return 200, [(b'content-type', b'text/plain')], text_writer('This is not a test')
```

The response is a tuple of the staus code, a list of headers, and an async byyes generator for the response body.

The `scope` is a dictionary which holds the request information, e.g. server, scheme, method, etc.

The `content` is an sync iterator of bytes. The are some utility functions for extracting strings.

### HttpMiddlewareCallback

The middleware callback adds an http request callback as the last argument.

```python
async def first_middleware(scope: Scope, info: Info, matches: RouteMatches, content: Content, handler: HttpRequestCallback ) -> HttpResponse:
    return await handler(scope, info, matches, content)
```

### WebSocketRequestCallback

The WebSocket request callback has the following form.

```python
async def test_callback(scope: Scope, info: Info, matches: RouteMatches, web_socket: WebSocket) -> None:
    ...
```

The WebSocket class it self has the following structure.

```python
class WebSocket:

    async def accept(self, subprotocol: Optional[str] = None) -> None:
        ...

    async def receive(self) -> Optional[Union[bytes, str]]:
        ...

    async def send(self, content: Union[bytes, str]) -> None:
        ...

    async def close(self, code: int = 1000) -> None:
        ...
```

The first call must be to acccept the socket.

## Utilities

There are a number of utility functions for reading content and writing the body.

```python
async bytes_reader(content: Content) -> bytes
async text_reader(content: Content, encoding: str = 'utf-8') -> str
async bytes_writer(buf: bytes) -> AsyncGenerator[bytes, None]
async text_writer(text: str, encoding: str = 'utf-8') -> AsyncGenerator[bytes, None]
```

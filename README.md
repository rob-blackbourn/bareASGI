# bareASGI

A lightweight ASGI framework (read the [documentation](https://bareasgi.readthedocs.io/en/latest/))

## Status

Work in progress.

## Overview

This is a _bare_ ASGI web server framework. The goal is to provide
a minimal implementation, with other facilities (serving static files, CORS, sessions, etc.)
being implemented by optional packages.

Some of the features provided by web frameworks are not required for a given app, or conflict with the
version or varient required for a given solution. 

See also:
* [bareASGI-cors](https://github.com/rob-blackbourn/bareasgi-cors) for cross origin resource sharing
* [bareASGI-static](https://github.com/rob-blackbourn/bareasgi-static) for static file serving
* [bareASGI-jinja2](https://github.com/rob-blackbourn/bareasgi-jinja2) for Jinja2 template rendering
* [bareASGI-graphql-next](https://github.com/rob-blackbourn/bareasgi-graphql-next) for GraphQL

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

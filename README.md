# bareASGI

A lightweight Python [ASGI](user-guide/asgi) web server framework
(read the [docs](https://rob-blackbourn.github.io/bareASGI/)).

## Overview

This is a _bare_ ASGI web server framework. The goal is to provide
a minimal implementation, with other facilities (serving static files, CORS,
sessions, etc.) being implemented by optional packages.

The framework is targeted at micro-services which require a light footprint, or
as a base for larger frameworks.

Python 3.7+ is required.

## Optional Packages

* [bareASGI-cors](https://github.com/rob-blackbourn/bareASGI-cors) for cross origin resource sharing,
* [bareASGI-static](https://github.com/rob-blackbourn/bareASGI-static) for serving static files,
* [bareASGI-jinja2](https://github.com/rob-blackbourn/bareASGI-jinja2) for [Jinja2](https://github.com/pallets/jinja) template rendering,
* [bareASGI-graphql-next](https://github.com/rob-blackbourn/bareASGI-graphql-next) for [GraphQL](https://github.com/graphql-python/graphql-core) and [grapehene](https://github.com/graphql-python/graphene),
* [bareASGI-rest](https://github.com/rob-blackbourn/bareASGI-rest) for REST support,
* [bareASGI-prometheus](https://github.com/rob-blackbourn/bareASGI-prometheus) for [prometheus](https://prometheus.io/) metrics,
* [bareASGI-session](https://github.com/rob-blackbourn/bareASGI-session) for sessions.

## Functionality

While lightweight, the framework contains all the functionality required for
developing sophisticated web applications including:

* Http (1.0, 1.1, 2, 3),
* WebSockets,
* A method and path based router,
* Middleware,
* Http 2 push,
* Streaming requests and responses.

## Simple Server

Here is a simple server with a request handler that returns some text.

```python
import uvicorn
from bareasgi import Application, text_writer

async def http_request_callback(scope, info, matches, content):
    return 200, [(b'content-type', b'text/plain')], text_writer('This is not a test')

app = Application()
app.http_router.add({'GET'}, '/', http_request_callback)

uvicorn.run(app, port=9009)
```

# bareASGI

A lightweight Python [ASGI](user-guide/asgi) web server framework
(read the [docs](https://rob-blackbourn.github.io/bareASGI/)).

## Overview

This is a _bare_ ASGI web server framework. The goal is to provide
a minimal implementation, with other facilities (serving static files, CORS,
sessions, etc.) being implemented by optional packages.

The framework is targeted at micro-services which require a light footprint
(in a container for example), or as a base for larger frameworks.

Python 3.8+ is required.

## Optional Packages

- [bareASGI-cors](https://github.com/rob-blackbourn/bareASGI-cors) for cross origin resource sharing,
- [bareASGI-static](https://github.com/rob-blackbourn/bareASGI-static) for serving static files,
- [bareASGI-jinja2](https://github.com/rob-blackbourn/bareASGI-jinja2) for [Jinja2](https://github.com/pallets/jinja) template rendering,
- [bareASGI-graphql-next](https://github.com/rob-blackbourn/bareASGI-graphql-next) for [GraphQL](https://github.com/graphql-python/graphql-core) and [graphene](https://github.com/graphql-python/graphene),
- [bareASGI-rest](https://github.com/rob-blackbourn/bareASGI-rest) for REST support,
- [bareASGI-prometheus](https://github.com/rob-blackbourn/bareASGI-prometheus) for [prometheus](https://prometheus.io/) metrics,
- [bareASGI-session](https://github.com/rob-blackbourn/bareASGI-session) for sessions.

## Functionality

The framework provides the basic functionality required for developing a web
application, including:

- Http,
- WebSockets,
- Routing,
- Lifecycle,
- Middleware

## Simple Server

Here is a simple server with a request handler that returns some text.

```python
import uvicorn
from bareasgi import Application, HttpRequest, HttpResponse, text_writer

async def example_handler(request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        200,
        [(b'content-type', b'text/plain')],
        text_writer('This is not a test')
    )

app = Application()
app.http_router.add({'GET'}, '/', example_handler)

uvicorn.run(app, port=9009)
```

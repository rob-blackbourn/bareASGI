# Lifespan

Lifespan events occur when the server starts up and shuts down.

On startup they can be used for initialization, or for starting long running
tasks. On shutdown they can clean up resources and provide graceful termination.

You can find the ASGI documentation
[here](https://asgi.readthedocs.io/en/latest/specs/lifespan.html).

The source code for the following example can be found
[here](../examples/lifespan_nt.py)
(and here [here](../examples/lifespan.py) with typing).

## Handlers

The following code creates an application with a startup and shutdown handler.

The handlers simply log a message.

```python
import asyncio
import logging

import uvicorn

from bareasgi import Application, text_writer

async def on_startup(scope, info, request):
    print("Running startup handler")

async def on_shutdown(scope, info, request):
    print("Running shutdown handler")

app = Application(
    startup_handlers=[on_startup],
    shutdown_handlers=[on_shutdown]
)

uvicorn.run(app, port=9009)
```

We can add the handlers at any point before the application starts (or stops
for shutdown handlers).

```python
app = Application()
app.startup_handlers.append(on_startup)
app.shutdown_handlers.append(on_shutdown)
```

We could have used a decorator instead.

```python
app = Application()

@app.on_startup
async def on_startup(scope, info, request):
    print("Running startup handler")
```

### Handler Parameters

#### Scope

The `scope` parameter contains the unmodified ASGI scope defined
[here](https://asgi.readthedocs.io/en/latest/specs/lifespan.html#scope).

It doesn't contain much that's useful, but I pass it for completeness.

#### Info

The `info` parameter contains the data that is shared across the application.

This is typically used to retrieve configuration, and store resources.

#### Request

The `request` is another unmodified piece of ASGI data, which contains the
content of the startup or shutdown event. This is also not particularly useful,
and is provided for completeness

## What next?

Either go back to the [table of contents](index.md) or go
to the [background tasks](background-tasks.md) tutorial.

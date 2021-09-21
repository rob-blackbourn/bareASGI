# Middleware

Middleware provides a means of applying common tasks to a request without having
to repeat the code.

For example one wanted to compress the output of request handlers, one might
add such middleware that would take the output of a request handler and compress
it. Another example would be authentication, The middleware could check if a
user had logged in before allowing the request handler to be called.

## Global middleware

The following example creates a chain of two middleware functions which add
content to a "message" provided by the `info` parameter.

The source code for the following example can be found
[here](../examples/global_middleware.py)
(and here [here](../examples/global_middleware.py) with typing).

```python
import uvicorn
from bareasgi import Application, text_writer


async def first_middleware(scope, info, matches, content, handler):
    print("First middleware - entry")
    info['message'] = 'This is first the middleware. '
    status, headers, response, pushes = await handler(
        scope,
        info,
        matches,
        content
    )
    print("First middleware - exit")
    return status, headers, response, pushes


async def second_middleware(scope, info, matches, content, handler):
    print("Second middleware - entry")
    info['message'] += 'This is the second middleware.'
    response = await handler(scope, info, matches, content)
    print("Second middleware - exit")
    return response


async def http_request_callback(scope, info, matches, content):
    return 200, [(b'content-type', b'text/plain')], text_writer(info['message'])

app = Application(
    middlewares=[
        first_middleware,
        second_middleware
    ]
)
app.http_router.add(
    {'GET', 'POST', 'PUT', 'DELETE'},
    '/',
    http_request_callback
)

uvicorn.run(app, port=9009)
```

The point at which the middleware is applied is on the application.

```python
app = Application(
    middlewares=[
        first_middleware,
        second_middleware
    ]
)
```

If we look at the first middleware function we can see it takes one more
argument, the `handler`, than a request handler.

```python
async def first_middleware(scope, info, matches, content, handler):
    print("First middleware - entry")
    info['message'] = 'This is first the middleware. '
    status, headers, response, pushes = await handler(
        scope,
        info,
        matches,
        content
    )
    print("First middleware - exit")
    return status, headers, response, pushes
```

The `handler` is the next function to call. We can see with the two print
statement that the middleware completely wraps the subsequent handler. This
gives us control of both the inputs and the outputs.

Inspecting the output of the program we can see the following results when we
browse to the page.

```
First middleware - entry
Second middleware - entry
Second middleware - exit
First middleware - exit
```
## Route local middleware

We can also apply the middleware to a specific route.

For example:

```python
from bareasgi.middleware import mw

...

app = Application(info={'message': 'Unmodified'})
app.http_router.add(
    {'GET', 'POST', 'PUT', 'DELETE'},
    '/with',
    mw(first_middleware, second_middleware, handler=http_request_callback)
)
app.http_router.add(
    {'GET', 'POST', 'PUT', 'DELETE'},
    '/without',
    http_request_callback
)
```

Now if we brows to http://localhost:9009/with we can see the middleware being
called, but when we browse to http://localhost:9009/without it is not.

The source code for this example can be found
[here](../examples/local_middleware.py)
(and here [here](../examples/local_middleware.py) with typing).

## What next?

Either go back to the [table of contents](index.md) or go
to the [WebSockets](websockets.md) tutorial.

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

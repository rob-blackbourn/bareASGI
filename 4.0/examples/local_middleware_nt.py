import uvicorn
from bareasgi import Application, HttpResponse, text_writer
from bareasgi import make_middleware_chain


async def first_middleware(request, handler):
    print("First middleware - entry")
    request.context['message'] = 'This is first the middleware. '
    response = await handler(request)
    print("First middleware - exit")
    return response


async def second_middleware(request, handler):
    print("Second middleware - entry")
    request.context['message'] += 'This is the second middleware.'
    response = await handler(request)
    print("Second middleware - exit")
    return response


async def http_request_callback(request):
    return HttpResponse(
        200,
        [(b'content-type', b'text/plain')],
        text_writer(request.context['message'])
    )


app = Application(info={'message': 'Unmodified'})
app.http_router.add(
    {'GET', 'POST', 'PUT', 'DELETE'},
    '/with',
    make_middleware_chain(first_middleware, second_middleware,
                          handler=http_request_callback)
)
app.http_router.add(
    {'GET', 'POST', 'PUT', 'DELETE'},
    '/without',
    http_request_callback
)

uvicorn.run(app, port=9009)

"""
An example of global middleware.
"""

from bareasgi import (
    Application,
    text_writer,
    HttpRequest,
    HttpResponse,
    HttpRequestCallback
)


async def first_middleware(
        request: HttpRequest,
        handler: HttpRequestCallback
) -> HttpResponse:
    """The first part of a middleware chain"""
    print("First middleware - entry")
    request.context['message'] = 'This is first the middleware. '
    response = await handler(request)
    print("First middleware - exit")
    return response


async def second_middleware(
        request: HttpRequest,
        handler: HttpRequestCallback
) -> HttpResponse:
    """The second part of a middleware chain"""
    print("Second middleware - entry")
    request.context['message'] += 'This is the second middleware.'
    response = await handler(request)
    print("Second middleware - exit")
    return response


async def http_request_callback(request: HttpRequest) -> HttpResponse:
    """The final request handler"""
    return HttpResponse(
        200,
        [(b'content-type', b'text/plain')],
        text_writer(request.context['message'])
    )


if __name__ == "__main__":
    import uvicorn

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

"""
Ann example of chaining middleware.
"""

import logging

from bareasgi import (
    Application,
    text_writer,
    HttpRequest,
    HttpResponse,
    HttpRequestCallback
)

logging.basicConfig(level=logging.DEBUG)


async def first_middleware(
        request: HttpRequest,
        handler: HttpRequestCallback
) -> HttpResponse:
    """The first part of a middleware chain"""
    request.info['message'] = 'This is first the middleware. '
    response = await handler(request)
    return response


async def second_middleware(
        request: HttpRequest,
        handler: HttpRequestCallback
) -> HttpResponse:
    """The second part of a middleware chain"""
    request.info['message'] += 'This is the second middleware.'
    response = await handler(request)
    return response


async def http_request_callback(request: HttpRequest) -> HttpResponse:
    """The final request handler"""
    return HttpResponse(
        200,
        [(b'content-type', b'text/plain')],
        text_writer(request.info['message'])
    )


if __name__ == "__main__":
    import uvicorn

    app = Application(middlewares=[first_middleware, second_middleware])
    app.http_router.add(
        {'GET', 'POST', 'PUT', 'DELETE'},
        '/{path}', http_request_callback
    )

    uvicorn.run(app, port=9009)

"""
An example of local middleware.
"""

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    text_writer,
    HttpResponse,
    HttpRequestCallback
)
from bareasgi.middleware import mw


async def first_middleware(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content,
        handler: HttpRequestCallback
) -> HttpResponse:
    """The first part of a middleware chain"""
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


async def second_middleware(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content,
        handler: HttpRequestCallback
) -> HttpResponse:
    """The second part of a middleware chain"""
    print("Second middleware - entry")
    info['message'] += 'This is the second middleware.'
    response = await handler(scope, info, matches, content)
    print("Second middleware - exit")
    return response


async def http_request_callback(
        _scope: Scope,
        info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    """The final request handler"""
    return 200, [(b'content-type', b'text/plain')], text_writer(info['message'])


if __name__ == "__main__":
    import uvicorn

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

    uvicorn.run(app, port=9009)

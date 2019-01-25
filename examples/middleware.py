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


async def first_middleware(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content,
        handler: HttpRequestCallback
) -> HttpResponse:
    info['message'] = 'This is first the middleware. '
    response = await handler(scope, info, matches, content)
    return response


async def second_middleware(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content,
        handler: HttpRequestCallback
) -> HttpResponse:
    info['message'] += 'This is the second middleware.'
    response = await handler(scope, info, matches, content)
    return response


async def http_request_callback(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    return 200, [(b'content-type', b'text/plain')], text_writer(info['message'])


if __name__ == "__main__":
    import uvicorn

    app = Application(middlewares=[first_middleware, second_middleware])
    app.http_router.add({'GET', 'POST', 'PUT', 'DELETE'}, '/{path}', http_request_callback)

    uvicorn.run(app, port=9009)

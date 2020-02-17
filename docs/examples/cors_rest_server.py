"""CORS REST server"""

import json
import logging

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    text_reader,
    text_writer
)
from bareasgi_cors import CORSMiddleware

logging.basicConfig(level=logging.DEBUG)


async def get_info(
        _scope: Scope,
        info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    """GET handler"""
    text = json.dumps(info)
    return 200, [(b'content-type', b'application/json')], text_writer(text)


async def set_info(
        _scope: Scope,
        info: Info,
        _matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """POST handler"""
    text = await text_reader(content)
    data = json.loads(text)
    info.update(data)
    return 204


if __name__ == "__main__":
    import uvicorn

    cors_middleware = CORSMiddleware()

    app = Application(
        info={'name': 'Michael Caine'},
        middlewares=[cors_middleware]
    )

    app.http_router.add({'GET'}, '/info', get_info)
    app.http_router.add({'POST', 'OPTIONS'}, '/info', set_info)

    uvicorn.run(app, port=9010)

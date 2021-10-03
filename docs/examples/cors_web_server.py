"""CORS web server"""

import logging

import pkg_resources
import uvicorn

from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)


async def http_request_callback(request: HttpRequest) -> HttpResponse:
    """Serve the html page"""
    page = request.info['html']
    return HttpResponse(
        200,
        [(b'content-type', b'text/html')],
        text_writer(page)
    )


if __name__ == "__main__":

    html_filename = pkg_resources.resource_filename(
        __name__,
        "cors_web_server.html"
    )
    with open(html_filename, 'rt', encoding='utf-8') as file_ptr:
        html = file_ptr.read()

    app = Application(info=dict(html=html))

    app.http_router.add({'GET'}, '/{path}', http_request_callback)

    uvicorn.run(app, port=9009)

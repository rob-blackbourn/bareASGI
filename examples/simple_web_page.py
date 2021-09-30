"""
A simple web page example
"""
import asyncio
import logging
import os
import socket

from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger('server_sent_events')


async def index(_request: HttpRequest) -> HttpResponse:
    """Redirect to the example"""
    return HttpResponse(303, [(b'Location', b'/example1')])


async def test_page1(_request: HttpRequest) -> HttpResponse:
    """A request handler which returns some html"""
    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Example 1</title>
  </head>
  <body>
    <h1>Example 1</h1>
    
    <p>This is simple<p>
  </body>
</html>

"""
    return HttpResponse(
        200,
        [(b'content-type', b'text/html')],
        text_writer(html)
    )


async def test_page2(_request: HttpRequest) -> HttpResponse:
    """A request handler which returns HTML"""
    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Example 2</title>
  </head>
  <body>
    <h1>Example 2</h1>

    <p>This is simple<p>
  </body>
</html>
"""
    return HttpResponse(
        200,
        [(b'content-type', b'text/html')],
        text_writer(html)
    )


async def test_empty(_request: HttpRequest) -> HttpResponse:
    """A request handler which only returns a valid "no content" status"""
    return HttpResponse(204)


if __name__ == "__main__":
    app = Application()

    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/example1', test_page1)
    app.http_router.add({'GET'}, '/example2', test_page2)
    app.http_router.add({'GET'}, '/empty', test_empty)

    import uvicorn
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    logging.basicConfig(level=logging.DEBUG)

    USE_UVICORN = False
    hostname = socket.gethostname()
    certfile = os.path.expanduser(f"~/.keys/server.crt")
    keyfile = os.path.expanduser(f"~/.keys/server.key")

    if USE_UVICORN:
        uvicorn.run(app, host='0.0.0.0', port=9009,
                    ssl_keyfile=keyfile, ssl_certfile=certfile)
    else:
        config = Config()
        config.bind = ["0.0.0.0:9009"]
        config.loglevel = 'debug'
        config.certfile = certfile
        config.keyfile = keyfile
        # config.verify_flags = ssl.VERIFY_X509_TRUSTED_FIRST
        # config.verify_mode = ssl.CERT_NONE
        # config.ciphers = "TLSv1"
        asyncio.run(serve(app, config))  # type: ignore
        # Options.OP_ALL|OP_NO_SSLv3|OP_NO_SSLv2|OP_CIPHER_SERVER_PREFERENCE|OP_SINGLE_DH_USE|OP_SINGLE_ECDH_USE|OP_NO_COMPRESSION

"""
REST style examples.
"""

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

logging.basicConfig(level=logging.DEBUG)


# pylint: disable=unused-argument
async def get_info(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """Write out the info a dictionary as JSON"""
    text = json.dumps(info)
    return 200, [(b'content-type', b'application/json')], text_writer(text)


# pylint: disable=unused-argument
async def set_info(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """Set the info dictionary to the posted JSON body"""
    text = await text_reader(content)
    data = json.loads(text)
    info.update(data)
    return 204


if __name__ == "__main__":

    app = Application(info={'name': 'Michael Caine'})
    app.http_router.add({'GET'}, '/test/api/info', get_info)
    app.http_router.add({'POST'}, '/test/api/info', set_info)

    import asyncio
    import uvicorn
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    import socket
    import os.path

    logging.basicConfig(level=logging.DEBUG)

    USE_UVICORN = False
    hostname = socket.gethostname()
    certfile = os.path.expanduser(f"~/.keys/{hostname}.crt")
    keyfile = os.path.expanduser(f"~/.keys/{hostname}.key")

    if USE_UVICORN:
        uvicorn.run(app, host='0.0.0.0', port=9009,
                    ssl_keyfile=keyfile, ssl_certfile=certfile)
    else:
        config = Config()
        config.bind = ["0.0.0.0:9009"]
        config.loglevel = 'debug'
        config.certfile = certfile
        config.keyfile = keyfile
        asyncio.run(serve(app, config))

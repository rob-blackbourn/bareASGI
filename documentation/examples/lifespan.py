"""A lifespan example."""

import asyncio
import logging
import signal
from typing import Any, List

from hypercorn.asyncio import serve
from hypercorn.config import Config
import uvicorn

from baretypes import (
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    Message,
    Header
)

from bareasgi import (
    Application,
    text_writer,
)

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)


async def on_startup(
        _scope: Scope,
        _info: Info,
        _request: Message
) -> None:
    """Run at startup"""
    LOGGER.info("Running startup handler")


async def on_shutdown(
        _scope: Scope,
        _info: Info,
        _request: Message
) -> None:
    """Run on shutdown"""
    LOGGER.info("Running shutdown handler")


async def http_request_callback(
        _scope: Scope,
        _info: Info,
        _matches: RouteMatches,
        _content: Content
) -> HttpResponse:
    """A request handler which returns some text"""
    headers: List[Header] = [
        (b'content-type', b'text/plain')
    ]
    return 200, headers, text_writer('This is not a test')


app = Application(
    startup_handlers=[on_startup],
    shutdown_handlers=[on_shutdown]
)
app.http_router.add({'GET'}, '/', http_request_callback)

# HTTP_SERVER = "uvicorn"
HTTP_SERVER = "hypercorn"

if HTTP_SERVER == "uvicorn":
    uvicorn.run(app, port=9009)
elif HTTP_SERVER == "hypercorn":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    shutdown_event = asyncio.Event()

    def _signal_handler(*_: Any) -> None:
        shutdown_event.set()
    loop.add_signal_handler(signal.SIGTERM, _signal_handler)
    loop.add_signal_handler(signal.SIGINT, _signal_handler)

    config = Config()
    config.bind = ["0.0.0.0:9009"]
    loop.run_until_complete(
        serve(
            app,
            config,
            shutdown_trigger=shutdown_event.wait  # type: ignore
        )
    )

"""A lifespan example."""

import asyncio
import logging
from typing import Any

from baretypes import (
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpResponse,
    Message
)

from bareasgi import (
    Application,
    text_writer,
)

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)


async def on_startup(_scope: Scope, _info: Info, _request: Message) -> None:
    """Run at startup"""
    LOGGER.info("Running startup handler")


async def on_shutdown(_scope: Scope, _info: Info, _request: Message) -> None:
    """Run on shutdown"""
    LOGGER.info("Running shutdown handler")

# pylint: disable=unused-argument


async def http_request_callback(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A request handler which returns some text"""
    return 200, [(b'content-type', b'text/plain')], text_writer('This is not a test')


if __name__ == "__main__":
    app = Application(
        startup_handlers=[on_startup],
        shutdown_handlers=[on_shutdown]
    )
    app.http_router.add({'GET'}, '/{rest:path}', http_request_callback)

    USE_UVICORN = True

    if USE_UVICORN:
        import uvicorn
        uvicorn.run(app, port=9009)
    else:
        import signal
        import uvloop
        from hypercorn.asyncio import serve
        from hypercorn.config import Config
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
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

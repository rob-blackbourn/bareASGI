import asyncio
import logging
import signal

from hypercorn.asyncio import serve
from hypercorn.config import Config
import uvicorn

from bareasgi import Application, text_writer

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)


async def on_startup(scope, info, request):
    LOGGER.info("Running startup handler")


async def on_shutdown(scope, info, request):
    LOGGER.info("Running shutdown handler")


async def http_request_callback(scope, info, matches, content):
    headers = [
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

    def _signal_handler(*_):
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

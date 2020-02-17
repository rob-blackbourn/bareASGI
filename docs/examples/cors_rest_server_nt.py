import json
import logging

import uvicorn

from bareasgi import Application, text_reader, text_writer
from bareasgi_cors import CORSMiddleware

logging.basicConfig(level=logging.DEBUG)


async def get_info(scope, info, matches, content):
    text = json.dumps(info)
    return 200, [(b'content-type', b'application/json')], text_writer(text)


async def set_info(scope, info, matches, content):
    text = await text_reader(content)
    data = json.loads(text)
    info.update(data)
    return 204


cors_middleware = CORSMiddleware()

app = Application(
    info={'name': 'Michael Caine'},
    middlewares=[cors_middleware]
)

app.http_router.add({'GET'}, '/info', get_info)
app.http_router.add({'POST', 'OPTIONS'}, '/info', set_info)

uvicorn.run(app, port=9010)

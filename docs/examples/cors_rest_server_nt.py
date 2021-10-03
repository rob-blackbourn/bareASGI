import json
import logging

import uvicorn

from bareasgi import Application, HttpResponse, text_reader, text_writer
from bareasgi_cors import CORSMiddleware

logging.basicConfig(level=logging.DEBUG)


async def get_info(request):
    text = json.dumps(request.info)
    return HttpResponse(200, [(b'content-type', b'application/json')], text_writer(text))


async def set_info(request):
    text = await text_reader(request.body)
    data = json.loads(text)
    request.info.update(data)
    return HttpResponse(204)


cors_middleware = CORSMiddleware()

app = Application(
    info={'name': 'Michael Caine'},
    middlewares=[cors_middleware]
)

app.http_router.add({'GET'}, '/info', get_info)
app.http_router.add({'POST', 'OPTIONS'}, '/info', set_info)

uvicorn.run(app, port=9010)

"""Simple REST"""

import asyncio
import json

from hypercorn.asyncio import serve
from hypercorn.config import Config
from bareasgi import (
    Application,
    HttpResponse,
    text_reader,
    text_writer
)
from bareutils import header


async def get_info(request):
    """Handle the GET request"""
    accept = header.find(b'accept', request.scope['headers'])
    if accept != b'application/json':
        return HttpResponse(500)
    text = json.dumps(request.info)
    headers = [
        (b'content-type', b'application/json')
    ]
    return HttpResponse(200, headers, text_writer(text))


async def set_info(request):
    """Handle the POST request"""
    content_type = header.find(b'content-type', request.scope['headers'])
    if content_type != b'application/json':
        return HttpResponse(500)
    text = await text_reader(request.body)
    data = json.loads(text)
    request.info.update(data)
    return HttpResponse(204)

app = Application(info={'name': 'Michael Caine'})
app.http_router.add({'GET'}, '/info', get_info)
app.http_router.add({'POST'}, '/info', set_info)

config = Config()
config.bind = ["0.0.0.0:9009"]
asyncio.run(serve(app, config))  # type: ignore

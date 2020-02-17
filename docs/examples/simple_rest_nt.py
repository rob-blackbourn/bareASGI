import asyncio
import json

from hypercorn.asyncio import serve
from hypercorn.config import Config
from bareasgi import Application, text_reader, text_writer
import bareutils.header as header


async def get_info(scope, info, matches, content):
    accept = header.find(b'accept', scope['headers'])
    if accept != b'application/json':
        return 500
    text = json.dumps(info)
    headers = [
        (b'content-type', b'application/json')
    ]
    return 200, headers, text_writer(text)


async def set_info(scope, info, matches, content):
    content_type = header.find(b'content-type', scope['headers'])
    if content_type != b'application/json':
        return 500
    text = await text_reader(content)
    data = json.loads(text)
    info.update(data)
    return 204

app = Application(info={'name': 'Michael Caine'})
app.http_router.add({'GET'}, '/info', get_info)
app.http_router.add({'POST'}, '/info', set_info)

config = Config()
config.bind = ["0.0.0.0:9009"]
asyncio.run(serve(app, config))

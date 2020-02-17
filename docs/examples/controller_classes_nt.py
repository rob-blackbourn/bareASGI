import json
from bareasgi import Application, text_reader, text_writer
import uvicorn

class InfoController:

    def add_routes(self, app):
        app.http_router.add({'GET'}, '/info', self.get_info)
        app.http_router.add({'POST'}, '/info', self.set_info)

    async def get_info(self, scope, info, matches, content):
        text = json.dumps(info)
        return 200, [(b'content-type', b'application/json')], text_writer(text)

    async def set_info(self, scope, info, matches, content):
        text = await text_reader(content)
        data = json.loads(text)
        info.update(data)
        return 204

application = Application(info={'name': 'Michael Caine'})

info_controller = InfoController()
info_controller.add_routes(application)

uvicorn.run(application, port=9009)

import json
from bareasgi import Application, HttpResponse, text_reader, text_writer
import uvicorn


class InfoController:

    def add_routes(self, app):
        app.http_router.add({'GET'}, '/info', self.get_info)
        app.http_router.add({'POST'}, '/info', self.set_info)

    async def get_info(self, request):
        text = json.dumps(request.info)
        return HttpResponse(200, [(b'content-type', b'application/json')], text_writer(text))

    async def set_info(self, request):
        text = await text_reader(request.body)
        data = json.loads(text)
        request.info.update(data)
        return HttpResponse(204)


application = Application(info={'name': 'Michael Caine'})

info_controller = InfoController()
info_controller.add_routes(application)

uvicorn.run(application, port=9009)

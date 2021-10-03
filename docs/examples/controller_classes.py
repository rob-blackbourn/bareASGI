"""An example of using a class as a controller for route handling.
"""

import json
import logging

from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    text_reader,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)


class InfoController:
    """A controller which modifies the info property of the Application"""

    def add_routes(self, app: Application) -> None:
        """Add routes

        :param app: The application
        """
        app.http_router.add({'GET'}, '/info', self.get_info)
        app.http_router.add({'POST'}, '/info', self.set_info)

    async def get_info(self, request: HttpRequest) -> HttpResponse:
        """A response handler which returns the content of the info property as json"""
        text = json.dumps(request.info)
        return HttpResponse(
            200,
            [(b'content-type', b'application/json')],
            text_writer(text)
        )

    async def set_info(self, request: HttpRequest) -> HttpResponse:
        """A response handle which updates the info property with a json payload"""
        text = await text_reader(request.body)
        data = json.loads(text)
        request.info.update(data)
        return HttpResponse(204)


if __name__ == "__main__":
    import uvicorn

    application = Application(info={'name': 'Michael Caine'})

    info_controller = InfoController()
    info_controller.add_routes(application)

    uvicorn.run(application, port=9009)

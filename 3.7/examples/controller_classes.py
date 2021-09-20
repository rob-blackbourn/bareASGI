"""An example of using a class as a controller for route handling.
"""

import json
import logging

from bareasgi import (
    Application,
    Scope,
    Info,
    RouteMatches,
    Content,
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

    # pylint: disable=unused-argument
    async def get_info(
            self,
            scope: Scope,
            info: Info,
            matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        """A response handler which returns the content of the info property as json"""
        text = json.dumps(info)
        return 200, [(b'content-type', b'application/json')], text_writer(text)

    # pylint: disable=unused-argument
    async def set_info(
            self,
            scope: Scope,
            info: Info,
            matches: RouteMatches,
            content: Content
    ) -> HttpResponse:
        """A response handle which updates the info property with a json payload"""
        text = await text_reader(content)
        data = json.loads(text)
        info.update(data)
        return 204


if __name__ == "__main__":
    import uvicorn

    # pylint: disable=invalid-name
    application = Application(info={'name': 'Michael Caine'})

    info_controller = InfoController()
    info_controller.add_routes(application)

    uvicorn.run(application, port=9009)

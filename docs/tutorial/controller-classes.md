# Controller Classes

Sometimes it can be useful to group route handlers into a class, commonly
called a _controller_. This is often done when the controller has some state,
or dedicated access to a resource. For example a blog post controller might
hold a the instance of a blog post repository.

The source code for the following example can be found
[here](../examples/controller_classes_nt.py)
(and here [here](../examples/controller_classes.py) with typing).

The following snippet shows a trival example:

```python
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
```

## What next?

Either go back to the [table of contents](index.md) or go
to the [exceptions](exceptions.md) tutorial.

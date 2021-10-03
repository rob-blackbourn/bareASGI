# Usage

The following trival example uses the [uvicorn](https://www.uvicorn.org/)
server. See [here](user-guid/examples)
for more.

```python
import uvicorn
import json
from bareasgi import Application, HttpResponse, text_reader, text_writer

async def get_info(request):
    text = json.dumps(request.info)
    return HttpResponse(200, [(b'content-type', b'application/json')], text_writer(text))

async def set_info(request):
    text = await text_reader(request.body)
    data = json.loads(text)
    request.info.update(data)
    return HttpResponse(204)

app = Application(info={'name': 'Michael Caine'})
app.http_router.add({'GET'}, '/info', get_info)
app.http_router.add({'POST'}, '/info', set_info)

uvicorn.run(app, port=9009)
```

The above example demonstrates some of the key features of this implementation.

- All the handler takes a single request.
- Arguments like `scope` are passed directly from the ASGI server without being
  processed into helper classes.
- All features (even JSON encoding) are the responsibility of the application,
  not the framework.
- Handlers are asynchronous. The `text_writer` function is a simple wrapper
  which turns text into an async byte stream.

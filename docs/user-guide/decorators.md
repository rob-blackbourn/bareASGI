# Decorators

For small applications it can be more convenient to use decorators for
add route and lifespan handlers.

Here's a quick example:

```python
import uvicorn

from bareasgi import Application, HttpResponse, text_writer

app = Application()

@app.on_startup
async def my_startup_handler(request):
    print('Starting up')

@app.on_shutdown
async def my_shutdown_handler(request):
    print('Shutting down')

@app.on_http_request({'GET'}, '/{rest:path}')
async def http_request_callback(request):
    return HttpResponse(200, [(b'content-type', b'text/plain')], text_writer('This is not a test'))

uvicorn.run(app, port=9009)
```

import uvicorn
from bareasgi import Application, HttpResponse, text_writer

app = Application()


@app.on_http_request({'GET'}, '/')
async def http_request_handler(_request):
    return HttpResponse(200, [(b'content-type', b'text/plain')], text_writer('Hello, World!'))

uvicorn.run(app, port=9009)

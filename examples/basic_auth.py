"""An example of basic authentication"""

from base64 import b64decode

import uvicorn
from bareutils import header, response_code, text_writer
from bareasgi import Application, HttpRequest, HttpResponse

async def authenticate(request: HttpRequest) -> HttpResponse:
    authorization = header.authorization(request.scope['headers'])
    if not authorization:
        return HttpResponse(response_code.UNAUTHORIZED)
    
    _auth_type, credentials = authorization
    username, _sep, password = b64decode(credentials).partition(b':')
    
    message = f'Authenticated {username.decode()} with password {password.decode()}.'

    return HttpResponse(
        response_code.OK,
        [(b'content-type', b'text/plain')],
        text_writer(message)
    )


if __name__ == "__main__":

    app = Application()
    app.http_router.add({'GET'}, '/authenticate', authenticate)

    uvicorn.run(app, port=9009)

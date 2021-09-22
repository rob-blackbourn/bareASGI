"""An example of sending and receiving cookies."""

import logging
from typing import Dict
from urllib.parse import parse_qsl

from bareutils import header

from bareasgi import (
    Application,
    HttpRequest,
    HttpResponse,
    text_reader,
    text_writer
)

logging.basicConfig(level=logging.DEBUG)

FORM_HTML = """
<!DOCTYPE html>
<html>
<body>

<h2>HTML Form</h2>

<form action="/post_form" method="post">
  First name:<br>
  <input type="text" name="first_name" value="{first_name}">
  <br>
  Last name:<br>
  <input type="text" name="last_name" value="{last_name}">
  <br><br>
  <input type="submit" value="Submit">
</form> 

<h2>Cookies</h2>

{cookies}

</body>
</html>
"""


async def index(_request: HttpRequest) -> HttpResponse:
    """Redirect to the test page"""
    return HttpResponse(303, [(b'Location', b'/get_form')])


async def get_form(request: HttpRequest) -> HttpResponse:
    """A response handler which returns a form and sets some cookies"""
    cookies = header.cookie(request.scope['headers'])

    first_name = cookies.get(b'first_name', [b'Micky'])[0]
    last_name = cookies.get(b'last_name', [b'Mouse'])[0]

    html_list = '<dl>'
    for name, values in cookies.items():
        for value in values:
            html_list += f'<dt>{name.decode()}</dt><dd>{value.decode()}</dd>'
    html_list += '</dl>'

    html = FORM_HTML.format(
        first_name=first_name.decode(),
        last_name=last_name.decode(),
        cookies=html_list
    )
    headers = [
        (b'content-type', b'text/html'),
    ]
    return HttpResponse(200, headers, text_writer(html))


async def post_form(request: HttpRequest) -> HttpResponse:
    """A response handler that reads the cookies from a posted form."""
    content_type = header.find(b'content-type', request.scope['headers'])
    if content_type != b'application/x-www-form-urlencoded':
        return HttpResponse(500)
    variables = await text_reader(request.body)
    values: Dict[str, str] = dict(parse_qsl(variables))
    first_name = values['first_name']
    last_name = values['last_name']

    headers = [
        (b'location', b'/get_form'),
        (b'set-cookie', f'first_name={first_name}'.encode()),
        (b'set-cookie', f'last_name={last_name}'.encode()),
    ]
    return HttpResponse(303, headers)


if __name__ == "__main__":
    import uvicorn

    app = Application()
    app.http_router.add({'GET'}, '/', index)
    app.http_router.add({'GET'}, '/get_form', get_form)
    app.http_router.add({'POST'}, '/post_form', post_form)

    uvicorn.run(app, port=9009)

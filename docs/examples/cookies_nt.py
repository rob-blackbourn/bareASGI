import logging
from urllib.parse import parse_qsl

import uvicorn

from bareasgi import Application, text_reader, text_writer
import bareutils.header as header

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

async def index(scope, info, matches, content):
    return 303, [(b'location', b'/get_form')]

async def get_form(scope, info, matches, content):
    cookies = header.cookie(scope['headers'])

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
    return 200, headers, text_writer(html)

async def post_form(scope, info, matches, content):
    content_type = header.find(b'content-type', scope['headers'])
    if content_type != b'application/x-www-form-urlencoded':
        return 500

    variables = await text_reader(content)
    values = dict(parse_qsl(variables))
    first_name = values['first_name']
    last_name = values['last_name']

    headers = [
        (b'location', b'/get_form'),
        (b'set-cookie', f'first_name={first_name}'.encode()),
        (b'set-cookie', f'last_name={last_name}'.encode()),
    ]
    return 303, headers

sapp = Application()
app.http_router.add({'GET'}, '/', index)
app.http_router.add({'GET'}, '/get_form', get_form)
app.http_router.add({'POST'}, '/post_form', post_form)

uvicorn.run(app, port=9009)

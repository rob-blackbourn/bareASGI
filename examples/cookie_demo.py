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
import bareasgi.header as header

logging.basicConfig(level=logging.DEBUG)

FORM = """
<!DOCTYPE html>
<html>
<body>

<h2>HTML Form</h2>

<form action="/post_form" method="post">
  First name:<br>
  <input type="text" name="firstname" value="Mickey">
  <br>
  Last name:<br>
  <input type="text" name="lastname" value="Mouse">
  <br><br>
  <input type="submit" value="Submit">
</form> 

<p>If you click the "Submit" button, the form-data will be sent to a page called "/action_page.php".</p>

</body>
</html>
"""

COOKIES = """
<!DOCTYPE html>
<html>
<body>

<h2>Cookies</h2>

{cookies}

</body>
</html>
"""


async def get_form(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    headers = [
        (b'content-type', b'text/html'),
        (b'set-cookie', b'first=first cookie'),
        (b'set-cookie', b'second=second cookie'),
    ]
    return 200, headers, text_writer(FORM)


async def post_form(scope: Scope, info: Info, matches: RouteMatches, content: Content) -> HttpResponse:
    cookies = header.cookie(scope['headers'])
    html_list = '<dl>'
    for name, values in cookies.items():
        for value in values:
            html_list += f'<dt>{name.decode()}</dt><dd>{value.decode()}</dd>'
    html_list += '</dl>'
    return 200, [(b'content-type', b'text/html')], text_writer(COOKIES.format(cookies=html_list))


if __name__ == "__main__":
    import uvicorn

    app = Application()
    app.http_router.add({'GET'}, '/get_form', get_form)
    app.http_router.add({'POST'}, '/post_form', post_form)

    uvicorn.run(app, port=9009)

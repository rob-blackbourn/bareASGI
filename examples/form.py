"""
An example using forms.
"""

import logging
import urllib.parse
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

FORM = """
<!DOCTYPE html>
<html>
<body>

<h2>HTML Forms</h2>

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


# pylint: disable=unused-argument
async def get_form(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A request handler which returns a form"""
    return 200, [(b'content-type', b'text/html')], text_writer(FORM)


# pylint: disable=unused-argument
async def post_form(
        scope: Scope,
        info: Info,
        matches: RouteMatches,
        content: Content
) -> HttpResponse:
    """A request handler for the form POST"""
    text = await text_reader(content)
    data = urllib.parse.parse_qs(text)
    print(data)
    return 200, [(b'content-type', b'text/plain')], text_writer('This is not a test')


if __name__ == "__main__":
    import uvicorn

    app = Application()
    app.http_router.add({'GET'}, '/get_form', get_form)
    app.http_router.add({'POST'}, '/post_form', post_form)

    uvicorn.run(app, port=9009)

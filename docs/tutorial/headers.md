# Headers (including cookies)

As you might expect, the support for sending and receiving headers is pretty
bare!

The ASGI servers send and receive headers as a list of 2-tuples of bytes, e.g.

```python
headers = [
    (b'content-type': b'application/json'),
    (b'set-cookie', b'first=first cookie')
]
```

Most templates preprocess these to dict fo lists of strings. However, I found
that in many cases I never even need to look at the headers, so it seemed like
an unnecessary overhead. The approach taken by this framework is to provide
some utility functions.

## bareUtils

The bareASGI package includes `bareUtils` as a dependency. Amongst other things
this provides utilities for headers. These are all pretty basic and I encourage
you to build your own.

The module I use the most is `bareUtils.header`.

```python
import bareUtils.header as header

accept = header.find(b'accept', scope['headers'])
content_type = header.find(b'content-type', scope['headers'], b'application/json')
cookies = header.find_all(b'cookie', scope['headers'])
```

In the above example the `accept` header would be searched for, or None if not
present. With the `find` function, the first matching entry is returned.
For `content-type` a default of `b'application/json'` is provided. In
the last example all headers of name `cookie` are returned in a list.

As you can see, no attempt is made to process the headers into dictionaries or
strings.

## Header Helpers

There are a number of helper methods written for the more common headers.

For example to retrieve the `content-type` the following function can be used.

```python
>>> import bareutils.header as header
>>> header.content_type([(b'content-type', b'text/html; charset=UTF-8')])
(b'text/html', {b'charset': b'UTF-8'})
```

## Cookies

The source code for the following example can be found
[here](../examples/cookies_nt.py)
(and here [here](../examples/cookies.py) with typing).

The key part of the code is where we set the cookies.

```python
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
```

This handler receives the `POST` from the form. First it checks that the content
type is appropriate for form data.

Then it reads the body and unpacks it. Note that there is no special support for
unpacking, we simply use the `urllib.parse.parse_sql` function from the standard
library.

Finally it sets the cookies with `set-cookie` in the headers. The `bareUtils`
package provides a utility function `encode_set_cookie` which we could have
used, but in this case it was unnecessary.

Here is the prototype for `encode_set_cookie`.

```python
def encode_set_cookie(
        name: bytes,
        value: bytes,
        *,
        expires: Optional[datetime] = None,
        max_age: Optional[Union[int, timedelta]] = None,
        path: Optional[bytes] = None,
        domain: Optional[bytes] = None,
        secure: bool = False,
        http_only: bool = False,
        same_site: Optional[bool] = None
) -> bytes:
    ...
```

There is a complimentary decode function.

```python
def decode_set_cookie(set_cookie: bytes) -> Mapping[str, Any]:
```

The form handler which presents the form looks like this:

```python
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
```

It uses another utility function `header.cookies` which simply packs the cookies
into a dict. Note that multiple cookies of the same name may be passed.


## What next?

Either go back to the [table of contents](index.md) or go
to the [cors](cors.md) tutorial.

# Simple REST

This example sends and receives data using REST. You will need something like
[postman](https://www.getpostman.com/) to try it out.

We use [hypercorn](https://pgjones.gitlab.io/hypercorn/) as the ASGI server.

The source code can be found
[here](../examples/hello_world_nt.py)
(and here [here](../examples/hello_world.py) with typing).

```python
import asyncio
import json

from hypercorn.asyncio import serve
from hypercorn.config import Config
from bareasgi import Application, text_reader, text_writer
import bareutils.header as header

async def get_info(scope, info, matches, content):
    accept = header.find(b'accept', scope['headers'])
    if accept != b'application/json':
        return 500
    # Get the info
    text = json.dumps(info)
    headers = [
        (b'content-type', b'application/json')
    ]
    return 200, headers, text_writer(text)

async def set_info(scope, info, matches, content):
    content_type = header.find(b'content-type', scope['headers'])
    if content_type != b'application/json':
        return 500
    text = await text_reader(content)
    data = json.loads(text)
    # Set the info
    info.update(data)
    return 204

app = Application(info={'name': 'Michael Caine'})
app.http_router.add({'GET'}, '/info', get_info)
app.http_router.add({'POST'}, '/info', set_info)

# Start hypercorn
config = Config()
config.bind = ["0.0.0.0:9009"]
asyncio.run(serve(app, config))
```

To try this out make a `GET` request to http://localhost:9009/info with the
`accept` header set to `application/json`. It should respond with a
`content-type` of `application/json` and *body* of `{“name": “Michael Caine"}`.
Sending a `POST` to the same endpoint with the body `{“name": “Peter Sellers"}`
and a `content-type` of `application/json` should respond with a `204` status
code. A subsequent `GET` should return `{“name": “Peter Sellers"}`.

## Request Parameters

In this example we start to use some of the request parameters. 

### Scope

The `scope` is passed directly from the ASGI server. It is a dictionary of
values describing the request. We use it here to inspect the headers.

Looking at the ASGI 
[cconnection-scope](https://asgi.readthedocs.io/en/latest/specs/www.html#connection-scope)
documentation we can see it contains everything the ASGI server knows about the
request, including the scheme, the query string, etc.

### Info

The `info` is a `dict` which is supplied to the `Application` on construction 
(or automatically generated if not). It is the means of the application sharing
data.

In this example it is created with a `name` entry.

```python
app = Application(info={'name': 'Michael Caine'})
```

The `GET` handler retrieves the `info` and returns it as a string.

```python
text = json.dumps(info)
headers = [
    (b'content-type', b'application/json')
]
return 200, headers, text_writer(text)
```

The `POST` handler reads the new data from the request body and updates the
`info` with whatever was sent.

```python
text = await text_reader(content)
data = json.loads(text)
info.update(data)
```

A subsequent `GET` will return the new content of info.

### Content

The `content` is the complement of the body in the response. It is another
asynchronous generator and is used to read the body of the request. The
`text_reader` helper function is used to retrieve the body (note this is
awaited).

## Response

The handlers respond with `500` if the request was incorrect.

```python
if content_type != b'application/json':
    return 500
```

We can see that it is not necessary to provide all the elements of the response,
where all elements to the right would be `None`.

## What next?

Either go back to the [table of contents](index.md) or go to the
[lifespan](lifespan.md) tutorial.

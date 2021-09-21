# Getting Started with bareASGI

## Prerequisites

### ASGI Servers

The [bareASGI](https://github.com/rob-blackbourn/bareasgi) package is a
web framework package for [ASGI](https://asgi.readthedocs.io/en/latest/)
servers, so the first thing required is a server.

The servers I have been using are:

* [hypercorn](https://pgjones.gitlab.io/hypercorn/)
* [uvicorn](https://www.uvicorn.org/)

At the time of writing hypercorn has the best support for HTTP/2, while
uvicorn is the most simple to use. Checkout the links above for installation
instructions,

The examples will use both servers.

### bareASGI

Finally we must install bareASGI. The bare libraries use
[poetry](https://poetry.eustace.io/), but you can just use pip if you prefer.

```bash
$ pip install bareasgi
```

### Visual Studio Code

I use [Visual Studio Code](https://code.visualstudio.com/) as my development
environment, and I have left the .vscode files with my settings and launch
configurations.

## Hello, World!

Here's a simple hello world program with a link to the source code [here](../examples/hello_world_nt.py), and here [here](../examples/hello_world.py) with typing.

```python
import uvicorn
from bareasgi import Application, bytes_writer

app = Application()

@app.on_http_request({'GET'}, '/')
async def http_request_handler(scope, info, matches, content):
    return 200, [(b'content-type', b'text/plain')], bytes_writer(b'Hello, World!')

uvicorn.run(app, port=9009)
```

Browsing to http://localhost:9009 will show "Hello, World!".

Now let’s take this apart.

### The HTTP Request Handler

As it’s name suggests the `http_request_handler` function handles an HTTP
*request*. It’s arguments form the request, and it returns a *response*. Unlike
other frameworks I chose not to wrap these in an object. There aren’t many, and
I took the view that the less work done that isn’t strictly necessary the faster
the framework would be.

This example doesn’t use any of the input parameters, so I’ll introduce them
later, but it does return a whole lot of stuff for the response.

### The HTTP Response

The first element of the response tuple is the **200** 
[HTTP response code](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status).

The second element are the headers. These are optional (we could have passed in
None), but we’re returning plain text so I set the `content-type` accordingly. 
Note that the headers are a list of tuples of bytes. Also the header name is in
lower case. This is all part of the ASGI standard, and it means this list can be
passed directly through to the server without the framework doing any extra
work.

The third element is the body of the response. This looks a bit tricksy, but
it’s one of the key concepts in the framework, so we’ll take a little time to
understand it. Here’s the actual code for `bytes_writer`.

```python
async def bytes_writer(buf, chunk_size = -1):
    if chunk_size == -1:
        yield buf
    else:
        start, end = 0, chunk_size
        while start < len(buf):
            yield buf[start:end]
            start, end = end, end + chunk_size
```

This is an *[asynchronous generator](https://www.python.org/dev/peps/pep-0525/)*.
It (optionally) splits the response into chunks which are sent to the client in
sequence. We do this for a number of reasons.

First it makes the generation of the response asynchronous. Lets say you’re
sending an image file. If the file is read asynchronously in chunks the asyncio
coroutines will be able to yield during the file chunk reading and when sending
the chunk over the network to the client. This means your web server will be
able to respond to other requests while the IO is waiting.

Second it means the response can be cancelled. If the client browses away from
the page before the image has been uploaded, the image data will stop being read
and the server will stop sending it.

Third we can support streaming content: for example a ticking price or a twitter
feed.

The last element of the response is a list of push request supported by the
HTTP/2 protocol which I won’t discuss that here.

### Routing

In the above example routing was implemented with a decorator:

```python
@app.on_http_request({'GET'}, '/hello-world')
```

The first argument is a set of HTTP methods that are supported by the handler,
and the second is the path to which the handler will respond.

I used the decorator routing style for simplicity, however it could have been
done in the following manner:

```python
import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config
from bareasgi import Application, bytes_writer
async def http_request_callback(scope, info, matches, content):
    headers = [
        (b'content-type', b'text/plain')
    ]
    return 200, headers, bytes_writer(b'Hello, World!')
app = Application()
app.http_router.add({'GET'}, '/hello-world')
config = Config()
config.bind = ["0.0.0.0:9009"]
asyncio.run(serve(app, config))
```

This is my preferred method, as it allows more control over the creation of the
Application object.

In the examples above we used a literal path. We could also have used a 
parameterised path:

```python
'/foo/{name}/{id:int}/{created:datetime:%Y-%m-%d}'
```

Note how the parameters can optionally have types, and some types can have parse
patterns. There is also the special parameter `{path}` which captures all
remaining path elements.

The captured parameters are passed into the HTTP request handler as the
`matches` argument which is a dict of the parameter names as keys for the
matched values.

## What next?

Either go back to the [table of contents](index.md) or go to the
[simple rest](simple-rest.md) tutorial.

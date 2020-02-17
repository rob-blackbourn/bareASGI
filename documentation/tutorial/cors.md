# Cross-Origin Resource Sharing

[Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
(CORS) is a way for a server to allow a client to access it's data in a browser.

To demonstrate the functionality we will need two web servers. One to provide
data, and a second to request the data.

The source code for the REST server can be found
[here](../examples/cors_rest_server_nt.py)
(and here [here](../examples/cors_rest_server.py) with typing).

The source code for the web server can be found
[here](../examples/cors_web_server_nt.py)
(and here [here](../examples/cors_web_server.py) with typing)
with the html
[here](../examples/cors_web_server.html).

## REST Server

There is very little required to add CORS support. All you need to do is add
the middleware.

```python
from bareasgi import Application, text_reader, text_writer
from bareasgi_cors import CORSMiddleware


cors_middleware = CORSMiddleware()

app = Application(
    middlewares=[cors_middleware]
)
```

### POST requests

When a browser makes a cross origin `POST` it will first make an `OPTIONS`
request. Some web frameworks will transparently handle this, but in the "bare"
tradition of this framework it is left to the developer to decide this.

However, typically, if you have added CORS support you probably wanted to add
the `OPTIONS` method to any `POST` route.

```python
cors_middleware = CORSMiddleware()

app = Application(
    info={'name': 'Michael Caine'},
    middlewares=[cors_middleware]
)

app.http_router.add({'GET'}, '/info', get_info)
app.http_router.add({'POST', 'OPTIONS'}, '/info', set_info)
```

Note that this is not required on a `GET`.

## Web Server

The web server doesn't need to do anything special.

The page the web server provides calls a `GET` when the page loads.
```javascript
window.onload = function() {
fetch('http://127.0.0.1:9010/info')
    .then(function(response) {
    return response.json();
    })
    .then(function(info) {
    const element = document.getElementById('info');
    element.value = info.name;
    });
}
```

And when the form is submitted it makes a `POST`.

```javascript
fetch('http://127.0.0.1:9010/info', {
    method: 'POST',
    headers: {
    'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
})
    .then(function(response) {
    console.log(response);
    return Promise.resolve('Done');
    });
```

You can check that it's working by commenting out the CORS middleware in the
REST server. The browser will reject the fetch requests.

## What next?

Either go back to the [table of contents](index.md) or go
to [Diversion: A Simple REST Blog](../blog-rest/README.md).

# ASGI

## What is ASGI?

An ASGI server sits at the front of a web application receiving and sending HTTP
and WebSocket messages. The client code simply sends and receives dictionaries
which describe the HTTP messages.

At it's heart ASGI is a specification. You can find the ASGI specification
[here](https://asgi.readthedocs.io/en/latest).

## Why?

Back in the days of Python 2 where there was no async/await functionality,
a lot of effort was required to make a responsive web server in python.
Essentially it was necessary to have a separate service which would create
a new process to service the request.

Out of this emerged the WSGI specification, and Python applications which
conformed to the specification could choose from a selection of servers
which supported the spec.

The ASGI specification is an asynchronous version of WSGI, which supports
the async/await functionlity of Python 3. This allows us to write a responsive
web service without the necessity of creating multiple processes, although
this may still be desirable for more performance.

## Servers

A number of servers have been written that support the specification. I have been using:

* [uvicorn](https://www.uvicorn.org/)
* [hypercorn](https://pgjones.gitlab.io/hypercorn/)

# HTTPS

While using https is not strictly a feature of this web framework, it's a
common requirement for two main reasons: for secure communication, and for
enabling HTTP/2.

## HTTP/2

The HTTP/2 protocol is now supported by all modern browsers, and removes a
number of significant performance problems. While not intrinsically
necessary, it is typically only used by browsers over an https connection.

## Certificates

There is a great deal of information on generating certificates online. I have
my own project which generates the certificates with a 
[makefile](https://github.com/rob-blackbourn/ssl-certs).

The following examples require a certificate in `$HOME/.keys/server.crt` and a key
in `$HOME/.keys/server.key`.

## Uvicorn

The code required for uvicorn is as follows.

```python
app = Application()

app.http_router.add({'GET'}, '/', test_page)

uvicorn.run(
    app,
    host='0.0.0.0',
    port=9009,
    ssl_certfile=os.path.expanduser(f"~/.keys/server.crt"),
    ssl_keyfile=os.path.expanduser(f"~/.keys/server.key")
)
```

The full source code for the example can be found
[here](../examples/https_uvicorn.py).

## Hypercorn

The code required for hypercorn is as follows:

```python
app = Application()

app.http_router.add({'GET'}, '/', test_page)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

shutdown_event = asyncio.Event()

def _signal_handler(*_: Any) -> None:
    shutdown_event.set()
loop.add_signal_handler(signal.SIGTERM, _signal_handler)
loop.add_signal_handler(signal.SIGINT, _signal_handler)

config = Config()
config.bind = ["0.0.0.0:9009"]
config.loglevel = 'debug'
config.certfile = os.path.expanduser(f"~/.keys/server.crt")
config.keyfile = os.path.expanduser(f"~/.keys/server.key")

loop.run_until_complete(
    serve(
        app,
        config,
        shutdown_trigger=shutdown_event.wait  # type: ignore
    )
)
```

The full source code for the example can be found
[here](../examples/https_hypercorn.py).

## What next?

Either go back to the [table of contents](index.md) or go
to the [middleware](middleware.md) tutorial.

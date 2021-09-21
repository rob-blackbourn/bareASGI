# SSL/HTTPS

## Overview

The following describes how to start some ASGI servers supporting SSL/HTTPS.

You can find information on creating self signed certificates
[here](https://medium.com/@rob.blackbourn/how-to-use-cfssl-to-create-self-signed-certificates-d55f76ba5781).

## Uvicorn

```python
import uvicorn

...

uvicorn.run(
    app,
    host='127.0.0.1',
    port=8008,
    ssl_keyfile='foo.key',
    ssl_certfile='foo.crt'
)
```

## Hypercorn

```python
import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config

...

web_config = Config()
web_config.bind = [ '0.0.0.0:8008' ]
web_config.keyfile = 'foo.key'
web_config.certfile = 'foo.crt'

asyncio.run(serve(app, web_config))
```

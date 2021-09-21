# Compression

Compression can be added through middleware.

The source code for the following example can be found
[here](../examples/compression_nt.py)
(and here [here](../examples/compression.py) with typing).

The middleware can be added as follows.

```python
from bareutils.compression import make_default_compression_middleware

compression_middleware = make_default_compression_middleware(minimum_size=1024)
app = Application(middlewares=[compression_middleware])
```

The middleware will then be applied according to the headers of the client
that made the request.

## What next?

Either go back to the [table of contents](index.md) or go
to the [controller classes](controller-classes.md) tutorial.

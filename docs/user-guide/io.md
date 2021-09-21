# Reading and Writing

Reading and writing body content is performed with asynchronous iterators and generators.

Note that the content is sent and received in bytes.

## Reading

Here is a simple example of a reader that consumes all the body content and returns a string.

```python
async def text_reader(content: Content) -> str:
    text = ''
    async for b in content:
        text += b.decode()
    return text
```

This mechanism means that no unnecessary work is done. For example if the content type was invalid it would be pointless
to decode the body. Also if inconsistent data was found an error can be returned rather than reading all the data.

## Writing

Here is a simple example of a reader that returns the body content as an async generator.

```python
async def text_writer(text: str) -> AsyncGenerator[bytes, None]:
    n = 512
    while text:
        yield text[:n].encode()
        text = text[n:]
```

Breaking up the message in this manner allows the ASGI server more control over the data sent. If the receiving client
decides to stop consuming the data, the remaining body need never be sent.

## Usage

We might use these functions in a handler in the following manner:

```python
async def set_info(scope, info, matches, content):
    text = await text_reader(content)
    return 204, None, text_writer(f'You said "{text}"')
```

Notice how the `text_reader` is awaited.

### Chunking

If content is sent without any headers an ASGI server will add the header
[transfer-encoding](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding)
set to `chunking`. In this mode the server will send out each part of the
body in **length prefixed** "chunks".

If the content length is known and a
[content-length](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Length)
header is set, the ASGI server will not add the chunked transfer encoding, but you can still send
the data in multiple parts.

If the content length is incorrect, the ASGI server will not help you, and the receiver will be
unable to properly receive the response.
from typing import AsyncGenerator
import codecs
from .types import Content


async def bytes_reader(content: Content) -> bytes:
    """Extracts the body content as bytes.

    :param content: The content argument of the request handler.
    :return: The body as bytes.
    """
    buf = b''
    async for b in content:
        buf += b
    return buf


async def text_reader(content: Content, encoding: str = 'utf-8') -> str:
    """Extracts the body contents as text.

    :param content: The content argument of the request handler.
    :param encoding: The encoding of the text (defaults to 'utf-8').
    :return: The body contents as a string.
    """
    codec_info: codecs.CodecInfo = codecs.lookup(encoding)
    decoder = codec_info.incrementaldecoder()
    text = ''
    async for b in content:
        text += decoder.decode(b)
    return text


async def bytes_writer(buf: bytes) -> AsyncGenerator[bytes, None]:
    """Creates an asynchronous generator from the supplied response body.

    :param buf: The response body to return.
    :return: An asynchronous generator of bytes.
    """
    yield buf


async def text_writer(text: str, encoding: str = 'utf-8') -> AsyncGenerator[bytes, None]:
    """Creates an asynchronous generator from the supplied response body.

    :param text: The response body.
    :param encoding:  The encoding to apply when transforming the text into bytes (defaults to 'utf-8').
    :return: An asynchronous generator of bytes.
    """
    yield text.encode(encoding=encoding)

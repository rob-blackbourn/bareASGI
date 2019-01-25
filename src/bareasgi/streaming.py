from typing import AsyncGenerator
import codecs
from .types import Content


async def bytes_reader(content: Content) -> bytes:
    buf = b''
    async for b in content:
        buf += b
    return buf


async def text_reader(content: Content, encoding: str = 'utf-8') -> str:
    codec_info: codecs.CodecInfo = codecs.lookup(encoding)
    decoder = codec_info.incrementaldecoder()
    text = ''
    async for b in content:
        text += decoder.decode(b)
    return text


async def bytes_writer(buf: bytes) -> AsyncGenerator[bytes, None]:
    yield buf


async def text_writer(text: str, encoding: str = 'utf-8') -> AsyncGenerator[bytes, None]:
    yield text.encode(encoding=encoding)

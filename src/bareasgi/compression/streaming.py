from abc import ABCMeta, abstractmethod
from typing import AsyncGenerator
import zlib
from ..streaming import bytes_writer


class Compressor(metaclass=ABCMeta):

    @abstractmethod
    def compress(self, buf: bytes) -> bytes:
        ...

    def flush(self) -> bytes:
        ...


def make_gzip_compressobj() -> Compressor:
    return zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)


def make_deflate_compressobj() -> Compressor:
    return zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)


def make_compress_compressobj() -> Compressor:
    return zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS)


async def compression_writer_adapter(
        writer: AsyncGenerator[bytes, None],
        compressobj: Compressor
) -> AsyncGenerator[bytes, None]:
    async for buf in writer:
        yield compressobj.compress(buf)
    yield compressobj.flush()


def compression_writer(
        buf: bytes,
        compressobj: Compressor,
        chunk_size: int = -1
) -> AsyncGenerator[bytes, None]:
    return compression_writer_adapter(bytes_writer(buf, chunk_size), compressobj)

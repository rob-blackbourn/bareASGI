from abc import ABCMeta, abstractmethod
from typing import AsyncGenerator
import zlib
from ..streaming import bytes_writer


class Compressor(metaclass=ABCMeta):
    """A class to represent the methods available on a compressor"""


    @abstractmethod
    def compress(self, buf: bytes) -> bytes:
        ...


    def flush(self) -> bytes:
        ...


def make_gzip_compressobj() -> Compressor:
    """Make a compressor for 'gzip'

    :return: A gzip compressor.
    """
    return zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)


def make_deflate_compressobj() -> Compressor:
    """Make a compressor for 'deflate'

    :return: A deflate compressor.
    """
    return zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)


def make_compress_compressobj() -> Compressor:
    """Make a compressor for 'compress'

    :return: A compress compressor.

    Note: This is not used by browsers anymore and should be avoided.
    """
    return zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS)


async def compression_writer_adapter(
        writer: AsyncGenerator[bytes, None],
        compressobj: Compressor
) -> AsyncGenerator[bytes, None]:
    """Adaptes a bytes generator to generated compressed output.

    :param writer: The writer to be adapted.
    :param compressobj: A compressor
    :return: A generator producing compressed output.
    """
    async for buf in writer:
        yield compressobj.compress(buf)
    yield compressobj.flush()


def compression_writer(
        buf: bytes,
        compressobj: Compressor,
        chunk_size: int = -1
) -> AsyncGenerator[bytes, None]:
    """Create an async generator for compressed content.

    :param buf: The bytes to compress
    :param compressobj: The compressor.
    :param chunk_size: An optional chunk size where -1 indicates no chunking.
    :return: An sync generator of compressed bytes.
    """
    return compression_writer_adapter(bytes_writer(buf, chunk_size), compressobj)

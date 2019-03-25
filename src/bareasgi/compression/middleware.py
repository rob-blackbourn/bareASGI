from typing import Mapping, List, Optional, Callable
from ..types import (
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpRequestCallback,
    HttpResponse
)
import bareasgi.header as header
from .streaming import (
    Compressor,
    compression_writer_adapter,
    make_deflate_compressobj,
    make_gzip_compressobj
)


class CompressionMiddleware:

    def __init__(self, compressors: Mapping[bytes, Callable[[], Compressor]], minimum_size: int = 512) -> None:
        """Constructs the compression middleware.

        :param compressors: A dictionary of encoding to compressor factories.
        :param minimum_size: The size below which no compression will be attempted.

        Note how the compression functions are passed rather than the compressors, as a fresh compressor
        is required for each message.

        .. code-block:: python

            compressors = {
                b'gzip': make_gzip_compressobj,
                b'deflate': make_deflate_compressobj
            }
            return CompressionMiddleware(compressors, minimum_size)
        """
        self.compressors = compressors
        self.minimum_size = minimum_size


    def is_acceptable(self, accept_encoding: Mapping[bytes, float], content_encoding: List[bytes]) -> bool:
        """Returns True if the requested encoding is acceptable.

        :param accept_encoding: The acceptable encodings.
        :param content_encoding: The current content encoding.
        :return: True if acceptable, otherwise False.

        If the quality value of 'identity' is specified as 0 we must support one of the other encodings.

        We must check the current encoding as it is possible that the this is already sufficient.
        """
        # Must the response be encoded?
        if accept_encoding[b'identity'] == 0.0:
            acceptable = {encoding for encoding, quality in accept_encoding.items() if quality != 0}
            current_encodings = {encoding for encoding in content_encoding if encoding != b'identity'}
            available = set(self.compressors.keys()) | current_encodings
            if len(acceptable & available) == 0:
                # No acceptable encodings are available.
                return False

        return True


    def is_desirable(
            self,
            accept_encoding: Mapping[bytes, float],
            content_encoding: List[bytes],
            content_length: Optional[int]
    ) -> bool:
        """Returns True if the compression is desirable.

        :param accept_encoding: The requested encodings.
        :param content_encoding: The current encoding.
        :param content_length: The content length if available.
        :return: True if compression is desirable, otherwise False.

        While compression might be possible it may not be desirable. For example the
        content may already be compresssed (e.g. for an image), or the content length
        may be too small to be worth the effort.
        """
        if content_length is not None and content_length < self.minimum_size:
            return False

        acceptable = {
            encoding
            for encoding, quality in accept_encoding.items()
            if quality != 0 and encoding != b'identity'
        }
        current = {
            encoding
            for encoding in content_encoding
            if encoding != b'identity'
        }

        if len(acceptable & current) > 0:
            # It's already encoded
            return False

        available = set(self.compressors.keys())
        if len(acceptable & available) == 0:
            # We don't have an available encoding
            return False

        return True


    def select_encoding(self, accept_encoding: Mapping[bytes, float]) -> bytes:
        acceptable = sorted([
            (encoding, quality)
            for encoding, quality in accept_encoding.items()
            if quality != 0 and encoding != b'identity'
        ], key=lambda x: x[1])

        return next(encoding for encoding, _ in acceptable if encoding in self.compressors)


    async def __call__(
            self,
            scope: Scope,
            info: Info,
            matches: RouteMatches,
            content: Content,
            handler: HttpRequestCallback
    ) -> HttpResponse:
        """Call the handler and compress the body if appropriate.

        :param scope: The scope passed through from the ASGI server.
        :param info: Application supplied information.
        :param matches: The route matches.
        :param content: The request content.
        :param handler: The handler to call and possibly compress the output of.
        :return: The response.
        """
        status, headers, body = await handler(scope, info, matches, content)

        if status < 200 or status >= 300:
            return status, headers, body

        accept_encoding = header.accept_encoding(scope['headers'], add_identity=True) or {b'identity': 1}
        content_encoding = header.content_encoding(headers) or [b'identity']

        if not self.is_acceptable(accept_encoding, content_encoding):
            return 406, None, None

        content_length = header.content_length(headers)
        if not self.is_desirable(accept_encoding, content_encoding, content_length):
            return status, headers, body

        vary = header.vary(headers) or []

        encoding = self.select_encoding(accept_encoding)

        # Copy the headers skipping the content-length, content-encoding, and vary.
        headers = [(k, v) for k, v in headers if k not in (b'content-length', b'content-encoding', b'vary')]

        # Add the content-encoding. We don't know the length, so the content length is omitted and chunking is used.
        headers.append((b'content-encoding', encoding))

        # Add accept-encoding to the vary header to indicate this is the same document regardless of the encoding.
        if b'accept-encoding' not in vary:
            vary.append(b'accept-encoding')
        headers.append((b'vary', b', '.join(vary)))

        # Get the compressor class.
        compressor_cls = self.compressors[encoding]

        # Return the response with the body wrappped in the compressor adapter.
        return status, headers, compression_writer_adapter(body, compressor_cls())


def make_default_compression_middleware(
        *,
        minimum_size: int = 512
) -> CompressionMiddleware:
    """Makes the compression middleware with the default compressors: gzip, and deflate.

    :param minimum_size: An optional size below which no compression is performed.
    :return: The compression middleware.

    The following adds the middleware, setting the minimum size to 1024

    .. code-black:: python

        compression_middleware = make_default_compression_middleware(minimum_size=1024)
        app = Application(middlewares=[compression_middleware])
    """
    compressors = {
        b'gzip': make_gzip_compressobj,
        b'deflate': make_deflate_compressobj
    }
    return CompressionMiddleware(compressors, minimum_size)

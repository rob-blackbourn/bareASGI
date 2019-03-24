from typing import Mapping, List
from ..types import (
    Scope,
    Info,
    RouteMatches,
    Content,
    HttpRequestCallback,
    HttpResponse
)
import bareasgi.header as header
from .streaming import Compressor, compression_writer_adapter


class CompressionMiddleware:

    def __init__(self, compressors: Mapping[bytes, Compressor]):
        self.compressors = compressors

    def is_acceptable(self, accept_encoding: Mapping[bytes, float], content_encoding: List[bytes]) -> bool:
        # Must the response be encoded?
        if accept_encoding[b'identity'] == 0.0:
            acceptable = {encoding for encoding, quality in accept_encoding.items() if quality != 0}
            current_encodings = {encoding for encoding in content_encoding if encoding != b'identity'}
            available = set(self.compressors.keys()) | current_encodings
            if len(acceptable & available) == 0:
                # No acceptable encodings are available.
                return False

        return True

    def is_desirable(self, accept_encoding: Mapping[bytes, float], content_encoding: List[bytes]) -> bool:
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

    def __call__(
            self,
            scope: Scope,
            info: Info,
            matches: RouteMatches,
            content: Content,
            handler: HttpRequestCallback
    ) -> HttpResponse:
        status, headers, body = await handler(scope, info, matches, content)

        if status < 200 or status >= 300:
            return status, headers, body

        accept_encoding = header.accept_encoding(scope['headers'], add_identity=True) or {b'identity': 1}
        content_encoding = header.content_encoding(scope['headers']) or [b'identity']

        if not self.is_acceptable(accept_encoding, content_encoding):
            return 406, None, None

        if not self.is_desirable(accept_encoding, content_encoding):
            return status, headers, body

        encoding = self.select_encoding(accept_encoding)

        headers = [(k, v) for k, v in headers if k not in (b'content-length', b'content-encoding')]
        headers.append((b'content-encoding', [encoding] + content_encoding))

        return status, headers, compression_writer_adapter(body, self.compressors[encoding])

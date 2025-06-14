"""The http response"""

from __future__ import annotations

from json import dumps
from typing import Any, AsyncIterable, Callable, Iterable

from bareutils import bytes_writer, text_writer

type PushResponse = tuple[str, list[tuple[bytes, bytes]]]


class HttpResponse:
    """The HTTP response"""

    def __init__(
            self,
            status: int,
            headers: list[tuple[bytes, bytes]] | None = None,
            body: AsyncIterable[bytes] | None = None,
            pushes: Iterable[PushResponse] | None = None
    ) -> None:
        """The HTTP response.

        Args:
            status (int): The status code.
            headers (list[tuple[bytes, bytes]] | None, optional): The headers
                if any. Mandatory headers will be added if missing. Defaults to
                None.
            body (AsyncIterable[bytes] | None, optional): The body, if any.
                Defaults to None.
            pushes (Iterable[PushResponse] | None, optional): Server pushes,
                if any. Defaults to None.
        """
        self.status = status
        self.headers = headers
        self.body = body
        self.pushes = pushes

    @classmethod
    def from_bytes(
            cls,
            content: bytes,
            *,
            status: int = 200,
            content_type: bytes = b'text/plain',
            headers: list[tuple[bytes, bytes]] | None = None,
            chunk_size: int = -1
    ) -> HttpResponse:
        """Create an HTTP response from bytes content.

        Args:
            content (bytes): The content.
            headers (list[tuple[bytes, bytes]] | None): Optional headers.
                Defaults to `None`.
            status (int, optional): An optional status. Defaults to `200`.
            content_type (bytes, optional): An optional content type. Defaults
                to `b'text/plain'`.
            chunk_size (int, optional): The size of each chunk to send or -1 to
                send as a single chunk. Defaults to -1.

        Returns:
            HttpResponse: The built HTTP response.
        """
        return HttpResponse(
            status,
            [(b'content-type', content_type)] + (headers or []),
            bytes_writer(content, chunk_size)
        )

    @classmethod
    def from_text(
            cls,
            text: str,
            *,
            status: int = 200,
            content_type: bytes = b'text/plain',
            headers: list[tuple[bytes, bytes]] | None = None,
            encoding: str = 'utf-8',
            chunk_size: int = -1
    ) -> HttpResponse:
        """Create an HTTP response from a text string.

        Args:
            text (str): A text string.
            headers (list[tuple[bytes, bytes]] | None): Optional headers.
                Defaults to `None`.
            status (int, optional): An optional status. Defaults to `200`.
            content_type (bytes, optional): An optional content type. Defaults
                to `b'text/plain'`.
            encoding (str, optional): The encoding to apply when transforming
                the text into bytes. Defaults to 'utf-8'.
            chunk_size (int, optional): The size of each chunk to send or -1 to
                send as a single chunk. Defaults to -1.

        Returns:
            HttpResponse: The built HTTP response.
        """
        return HttpResponse(
            status,
            [(b'content-type', content_type)] + (headers or []),
            text_writer(text, encoding, chunk_size)
        )

    @classmethod
    def from_json(
            cls,
            data: Any,
            *,
            status: int = 200,
            content_type: bytes = b'application/json',
            headers: list[tuple[bytes, bytes]] | None = None,
            encode: Callable[[Any], str] = dumps,
            encode_bytes: Callable[[Any], bytes] | None = None
    ) -> HttpResponse:
        """Create an HTTP response from data converted to JSON.

        Args:
            data (Any): The data to be converted to JSON.
            headers (list[tuple[bytes, bytes]] | None): Optional headers.
                Defaults to `None`.
            status (int, optional): An optional status code. Defaults to `200`.
            content_type (bytes, optional): An optional content type. Defaults
                to `b'application/json'`.
            encode (Callable[[Any], str], optional): An function to convert the
                data to a JSON string. Defaults to `json.dumps`.
            encode_bytes (Callable[[Any]], bytes] | None, optional): An
                optional function to convert the data to JSON bytes. If
                specified this will be preferred to the `encode` argument.
                Defaults to None.

        Returns:
            HttpResponse: A JSON http response.
        """
        return cls.from_bytes(
            encode_bytes(data),
            status=status,
            content_type=content_type,
            headers=headers
        ) if encode_bytes is not None else cls.from_text(
            encode(data),
            status=status,
            content_type=content_type,
            headers=headers
        )

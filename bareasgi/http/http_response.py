"""The http response"""

from __future__ import annotations

from json import dumps
from typing import Any, AsyncIterable, Callable, Iterable, List, Optional, Tuple

from bareutils import bytes_writer, text_writer

PushResponse = Tuple[str, List[Tuple[bytes, bytes]]]


class HttpResponse:
    """The HTTP response"""

    def __init__(
            self,
            status: int,
            headers: Optional[List[Tuple[bytes, bytes]]] = None,
            body: Optional[AsyncIterable[bytes]] = None,
            pushes: Optional[Iterable[PushResponse]] = None
    ) -> None:
        """The HTTP response.

        Args:
            status (int): The status code.
            headers (Optional[List[Tuple[bytes, bytes]]], optional): The headers
                if any. Mandatory headers will be added if missing. Defaults to
                None.
            body (Optional[AsyncIterable[bytes]], optional): The body, if any.
                Defaults to None.
            pushes (Optional[Iterable[PushResponse]], optional): Server pushes,
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
            headers: Optional[List[Tuple[bytes, bytes]]] = None,
            chunk_size: int = -1
    ) -> HttpResponse:
        """Create an HTTP response from bytes content.

        Args:
            content (bytes): The content.
            headers (Optional[List[Tuple[bytes, bytes]]]): Optional headers.
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
            headers: Optional[List[Tuple[bytes, bytes]]] = None,
            encoding: str = 'utf-8',
            chunk_size: int = -1
    ) -> HttpResponse:
        """Create an HTTP response from a text string.

        Args:
            text (str): A text string.
            headers (Optional[List[Tuple[bytes, bytes]]]): Optional headers.
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
            headers: Optional[List[Tuple[bytes, bytes]]] = None,
            encode: Callable[[Any], str] = dumps
    ) -> HttpResponse:
        """Create an HTTP response from data converted to JSON.

        Args:
            data (Any): The data to be converted to JSON.
            headers (Optional[List[Tuple[bytes, bytes]]]): Optional headers.
                Defaults to `None`.
            status (int, optional): An optional status code. Defaults to `200`.
            content_type (bytes, optional): An optional content type. Defaults
                to `b'application/json'`.
            encode (Callable[[Any], str], optional): An optional function to
                convert the data to a JSON string. Defaults to `json.dumps`.

        Returns:
            HttpResponse: _description_
        """
        return cls.from_text(
            encode(data),
            status=status,
            content_type=content_type,
            headers=headers
        )

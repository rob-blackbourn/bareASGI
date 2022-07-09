"""The http response"""

from __future__ import annotations

import json
from typing import Any, AsyncIterable, Callable, Iterable, List, Optional, Tuple

from bareutils import text_writer

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
    def from_text(
            cls,
            text: str,
            *,
            status: int = 200,
            content_type: bytes = b'text/plain',
            headers: Optional[List[Tuple[bytes, bytes]]] = None
    ) -> HttpResponse:
        """Create an HTTP response from a text string.

        Args:
            text (str): A text string.
            headers (Optional[List[Tuple[bytes, bytes]]]): Optional headers. Defaults
                to `None`.
            status (int, optional): An optional status. Defaults to `200`.
            content_type (bytes, optional): An optional content type. Defaults
                to `b'text/plain'`.

        Returns:
            HttpResponse: The built HTTP response.
        """
        return HttpResponse(
            status,
            [(b'content-type', content_type)] + (headers or []),
            text_writer(text)
        )

    @classmethod
    def from_json(
            cls,
            data: Any,
            *,
            status: int = 200,
            content_type: bytes = b'application/json',
            headers: Optional[List[Tuple[bytes, bytes]]] = None,
            dumps: Callable[[Any], str] = json.dumps
    ) -> HttpResponse:
        """Create an HTTP response from data converted to JSON.

        Args:
            data (Any): The data to be converted to JSON.
            headers (Optional[List[Tuple[bytes, bytes]]]): Optional headers. Defaults
                to `None`.
            status (int, optional): An optional status code. Defaults to `200`.
            content_type (bytes, optional): An optional content type. Defaults
                to `b'application/json'`.
            dumps (Callable[[Any], str], optional): An optional function to convert
                the data to a JSON string. Defaults to `json.dumps`.

        Returns:
            HttpResponse: _description_
        """
        return cls.from_text(
            dumps(data),
            status=status,
            content_type=content_type,
            headers=headers
        )

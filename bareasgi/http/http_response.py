"""The http response"""

from typing import AsyncIterable, Iterable, List, Optional, Tuple

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

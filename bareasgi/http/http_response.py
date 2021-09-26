"""The http response"""

from typing import AsyncIterable, Iterable, List, Optional, Tuple

PushResponse = Tuple[str, List[Tuple[bytes, bytes]]]


class HttpResponse:

    def __init__(
            self,
            status: int,
            headers: Optional[List[Tuple[bytes, bytes]]] = None,
            body: Optional[AsyncIterable[bytes]] = None,
            pushes: Optional[Iterable[PushResponse]] = None
    ) -> None:
        self.status = status
        self.headers = headers
        self.body = body
        self.pushes = pushes

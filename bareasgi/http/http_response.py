"""The http response"""

from typing import AsyncIterable, List, Optional, Tuple

from ..types import PushResponses


class HttpResponse:

    def __init__(
            self,
            status: int,
            headers: Optional[List[Tuple[bytes, bytes]]] = None,
            body: Optional[AsyncIterable[bytes]] = None,
            pushes: Optional[PushResponses] = None
    ) -> None:
        self.status = status
        self.headers = headers
        self.body = body
        self.pushes = pushes

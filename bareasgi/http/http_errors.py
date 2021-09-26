"""Types for bareASGI and bareClient"""

from typing import (
    AsyncIterable,
    List,
    Optional,
    Tuple,
    Union,
    cast
)

from bareutils import bytes_writer, text_writer


class HttpInternalError(Exception):
    """Exception raised for an internal error"""


class HttpDisconnectError(Exception):
    """Exception raise on HTTP disconnect"""


class HttpError(Exception):

    def __init__(
            self,
            status: int,
            message: Optional[Union[bytes, str, AsyncIterable[bytes]]] = None,
            url: Optional[str] = None,
            headers: Optional[List[Tuple[bytes, bytes]]] = None
    ) -> None:
        super().__init__()
        self.status = status
        self.url = url
        self.message = message
        self.headers = headers

    @property
    def body(self) -> Optional[AsyncIterable[bytes]]:
        if self.message is None:
            return None
        if hasattr(self.message, '__aiter__'):
            return cast(AsyncIterable[bytes], self.message)
        elif isinstance(self.message, bytes):
            return bytes_writer(self.message)
        elif isinstance(self.message, str):
            return text_writer(self.message)
        else:
            raise ValueError(
                'message must be bytes, str or AsyncIterable[bytes]')

        return self.message

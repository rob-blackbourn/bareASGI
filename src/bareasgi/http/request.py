"""The http request"""

from json import loads
from typing import Any, AsyncIterable, Callable, Mapping

from bareutils import header, bytes_reader, text_reader

from .typing import HTTPScope


class HttpRequest:
    """An HTTP request"""

    def __init__(
            self,
            scope: HTTPScope,
            info: dict[str, Any],
            context: dict[str, Any],
            matches: Mapping[str, Any],
            body: AsyncIterable[bytes]
    ) -> None:
        """An HTTP request.

        Args:
            scope (HTTPScope): The ASGI http scope.
            info (Dict[str, Any]): Shared data from the application.
            context (Dict[str, Any]): Private data for this request or chain of
                requests.
            matches (Mapping[str, Any]): Matches made by the router.
            body (AsyncIterable[bytes]): The body.
        """
        self.scope = scope
        self.info = info
        self.context = context
        self.matches = matches
        self.body = body

    @property
    def url(self) -> str:
        """Make the url from the scope.

        Returns:
            str: The url.
        """
        scheme = self.scope['scheme']
        host = header.find(b'host', self.scope['headers'], b'unknown')
        assert host is not None
        path = self.scope['path']
        return f"{scheme}://{host.decode()}{path}"

    async def text(self, encoding: str = 'utf-8') -> str:
        """Return the request body as text.

        This function consumes the body. Calling it a second time will generate
        an error.

        Args:
            encoding (str, optional): The encoding. Defaults to 'utf-8'.

        Returns:
            str: The body as text.
        """
        return await text_reader(self.body, encoding)

    async def content(self) -> bytes:
        """Return the contents of the request body as bytes.

        This function consumes the body. Calling it a second time will generate
        an error.

        Returns:
            bytes: The body as bytes.
        """
        return await bytes_reader(self.body)

    async def json(self, decode: Callable[[bytes], Any] = loads) -> Any:
        """Return the contents of the request body as JSON.

        This function consumes the body. Calling it a second time will generate
        an error.

        Args:
            decode (Callable[[Union[str, bytes]], Any], optional): A function to
                decode the body to json. Defaults to `json.loads`.

        Returns:
            Any: The body as JSON.
        """
        data = await self.content()
        return decode(data)

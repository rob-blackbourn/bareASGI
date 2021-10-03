"""The http request"""

from typing import Any, AsyncIterable, Dict, Mapping

from asgi_typing import HTTPScope
from bareutils import header


class HttpRequest:
    """An HTTP request"""

    def __init__(
            self,
            scope: HTTPScope,
            info: Dict[str, Any],
            context: Dict[str, Any],
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

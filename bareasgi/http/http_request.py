"""The http request"""

from typing import Any, AsyncIterable, Dict, Mapping

from bareutils import header

from ..types import Scope


class HttpRequest:

    def __init__(
            self,
            scope: Scope,
            info: Dict[str, Any],
            context: Dict[str, Any],
            matches: Mapping[str, Any],
            body: AsyncIterable[bytes]
    ) -> None:
        self.scope = scope
        self.info = info
        self.context = context
        self.matches = matches
        self.body = body

    @property
    def url(self) -> str:
        """Make the url from the scope"""
        scheme = self.scope['scheme']
        host = header.find(b'host', self.scope['headers'], b'unknown')
        assert host is not None
        path = self.scope['path']
        return f"{scheme}://{host.decode()}{path}"

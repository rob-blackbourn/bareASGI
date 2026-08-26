"""The abstract class for a websocket"""

from abc import ABCMeta, abstractmethod
from typing import Literal


WebSocketState = Literal['connected', 'open', 'closed']


class WebSocket(metaclass=ABCMeta):
    """The interface for a server side WebSocket."""

    @abstractmethod
    async def accept(
            self,
            subprotocol: str | None = None,
            headers: list[tuple[bytes, bytes]] | None = None
    ) -> None:
        """Accept the socket.

        This must be done before any other action is taken.

        Args:
            subprotocol (Optional[str], optional): An optional subprotocol sent
                by the client. Defaults to None.
            headers (Optional[List[Tuple[bytes, bytes]]], optional): Optional
                headers to send. Defaults to None.
        """

    @abstractmethod
    async def receive(self) -> bytes | str | None:
        """Receive data from the WebSocket.

        Returns:
            Optional[bytes | str]: Either bytes of a string depending on
                the client.
        """

    @abstractmethod
    async def send(self, content: bytes | str) -> None:
        """Send data to the client.

        Args:
            content (bytes | str): Either bytes or a string.
        """

    @abstractmethod
    async def close(self, code: int = 1000, reason: str | None = None) -> None:
        """Close the WebSocket.

        Args:
            code (int, optional): The reason code. Defaults to 1000.
            reason (str | None, optional): The reason. Can be any string.
                Defaults to 1000.
        """

    @abstractmethod
    async def wait_closed(self) -> None:
        """Wait until the connection is closed.
        """

    @property
    @abstractmethod
    def state(self) -> WebSocketState:
        """The state of the WebSocket lifecycle.

        Returns:
            WebSocketState: The state.
        """

    @property
    @abstractmethod
    def code(self) -> int:
        """The close code.

        Returns:
            int: The code the WebSocket was closed with.
        """

    @property
    @abstractmethod
    def reason(self) -> str | None:
        """The reason for the closure.

        Returns:
            str | None: The reason the WebSocket was closed.
        """

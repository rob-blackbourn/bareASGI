"""The abstract class for a websocket"""

from abc import ABCMeta, abstractmethod
from typing import (
    List,
    Optional,
    Tuple,
    Union
)


class WebSocket(metaclass=ABCMeta):
    """The interface for a server side WebSocket."""

    @abstractmethod
    async def accept(
            self,
            subprotocol: Optional[str] = None,
            headers: Optional[List[Tuple[bytes, bytes]]] = None
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
    async def receive(self) -> Optional[Union[bytes, str]]:
        """Receive data from the WebSocket.

        Returns:
            Optional[Union[bytes, str]]: Either bytes of a string depending on
                the client.
        """

    @abstractmethod
    async def send(self, content: Union[bytes, str]) -> None:
        """Send data to the client.

        Args:
            content (Union[bytes, str]): Either bytes or a string.
        """

    @abstractmethod
    async def close(self, code: int = 1000) -> None:
        """Close the WebSocket.

        Args:
            code (int, optional): The reason code. Defaults to 1000.
        """

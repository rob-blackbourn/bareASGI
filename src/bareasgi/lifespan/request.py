"""The lifespan request"""

from typing import Any, Awaitable, Callable

from .typing import LifespanScope


class LifespanRequest:
    """A class holding a lifespan request"""

    def __init__(
            self,
            scope: LifespanScope,
            info: dict[str, Any]
    ) -> None:
        """Initialise a class holding a lifespan request.

        Args:
            scope (LifespanScope): The ASGI lifespan scope.
            info (ASGILifespanReceiveEvent): The global info dictionary.
        """
        self.scope = scope
        self.info = info


type LifespanRequestHandler = Callable[[LifespanRequest], Awaitable[None]]

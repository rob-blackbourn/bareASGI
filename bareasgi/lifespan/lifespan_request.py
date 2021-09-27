"""
A handler of lifecycle event requests
"""

from typing import Any, Awaitable, Callable, Dict

from asgi_typing import LifespanScope


class LifespanRequest:
    """A class holding a lifespan request"""

    def __init__(
            self,
            scope: LifespanScope,
            info: Dict[str, Any]
    ) -> None:
        """Initialise a class holding a lifespan request

        Args:
            scope (LifespanScope): The ASGI lifespan scope.
            info (ASGILifespanReceiveEvent): The global info dictionary.
        """
        self.scope = scope
        self.info = info


LifespanRequestHandler = Callable[[LifespanRequest], Awaitable[None]]

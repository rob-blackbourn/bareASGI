"""
A handler of lifecycle event requests
"""

from typing import Any, Awaitable, Callable, Dict

from ..types import Scope


class LifespanRequest:
    """A class holding a lifespan request"""

    def __init__(
            self,
            scope: Scope,
            info: Dict[str, Any],
            message: Dict[str, Any]
    ) -> None:
        """Initialise a class holding a lifespan request

        Args:
            scope (Scope): The ASGI lifespan scope.
            info (Dict[str, Any]): The global info dictionary.
            message (Dict[str, Any]): The lifespan details.
        """
        self.scope = scope
        self.info = info
        self.message = message

# LifespanRequestHandler = Callable[[LifespanRequest], Coroutine[Any, Any, None]]
LifespanRequestHandler = Callable[[LifespanRequest], Awaitable[None]]

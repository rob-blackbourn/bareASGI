"""Types for bareASGI and bareClient"""

from typing import Any, Awaitable, Callable, Dict


Scope = Dict[str, Any]

Receive = Callable[[], Awaitable[Dict[str, Any]]]
Send = Callable[[Dict[str, Any]], Awaitable[None]]

ASGIInstance = Callable[[Receive, Send], Awaitable[None]]
ASGIApp = Callable[[Scope], ASGIInstance]

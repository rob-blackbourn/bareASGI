"""ASGI Versions"""

from typing import Literal, TypedDict


class ASGIVersions(TypedDict, total=False):
    """Version of the ASGI spec.

    Attributes:
        version (str): The version of the ASGI spec.
        spec_version (Literal["2.0"] | Literal["3.0"]): Version of the
            ASGI HTTP spec this server understands; one of `"2.0"` or `"2.1"`.
            Optional; if missing assume `"2.0"`.
    """
    spec_version: str
    version: Literal["2.0"] | Literal["3.0"]

"""Utilities"""

from datetime import datetime
import re
from typing import (
    Callable,
    Generic,
    Optional,
    Pattern,
    Tuple,
    TypeVar
)

T = TypeVar('T')


class NullIter(Generic[T]):
    """An iterator conttaining no items"""

    def __aiter__(self):
        return self

    async def __anext__(self) -> T:
        raise StopAsyncIteration


DateTimeFormat = Tuple[str, Pattern, Optional[Callable[[str], str]]]

DATETIME_FORMATS: Tuple[DateTimeFormat, ...] = (
    (
        "%Y-%m-%dT%H:%M:%SZ",
        re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'),
        None
    ),
    (
        "%Y-%m-%dT%H:%M:%S.%fZ",
        re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z$'),
        None
    ),
    (
        "%Y-%m-%dT%H:%M:%S%z",
        re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$'),
        lambda s: s[0:-3] + s[-2:]
    ),
    (
        "%Y-%m-%dT%H:%M:%S.%f%z",
        re.compile(
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{2}:\d{2}$'
        ),
        lambda s: s[0:-3] + s[-2:]
    )
)


def parse_json_datetime(value: str) -> Optional[datetime]:
    """Parse a JSON datetime.

    Args:
        value (str): The text to parse.

    Returns:
        Optional[datetime]: The parsed datetime or None.
    """
    if isinstance(value, str):
        for fmt, pattern, transform in DATETIME_FORMATS:
            if pattern.match(value):
                timestamp = transform(value) if transform else value
                return datetime.strptime(timestamp, fmt)
    return None

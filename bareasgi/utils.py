"""
Utilities
"""

from datetime import datetime
from decimal import Decimal
import json
import re
from typing import (
    Any,
    Callable,
    Generic,
    MutableMapping,
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


def json_datetime_parser(
        dct: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Convert JSON datetimes in a dictionary.

    Args:
        dct (MutableMapping[str, Any]): The dictionary.

    Returns:
        MutableMapping[str, Any]: The converted dictionary.
    """
    for key, value in dct.items():
        timestamp = parse_json_datetime(value)
        if timestamp:
            dct[key] = timestamp
    return dct


class JSONEncoderEx(json.JSONEncoder):
    """A JSON encoder that supports datetime and decimal conversion"""

    def default(self, obj):  # pylint: disable=arguments-renamed
        if isinstance(obj, datetime):
            return obj.isoformat() + ('Z' if not obj.tzinfo else '')
        elif isinstance(obj, Decimal):
            return float(
                str(
                    obj.quantize(Decimal(1))
                    if obj == obj.to_integral()
                    else obj.normalize()
                )
            )
        else:
            return super(JSONEncoderEx, self).default(obj)

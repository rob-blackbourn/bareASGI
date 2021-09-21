"""
Utilities
"""

from datetime import datetime
from decimal import Decimal
import json
import re
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Optional,
    MutableMapping,
    Pattern,
    Callable,
    Tuple
)


async def aiter(*args):
    """aiter(async_iterable) -> async_iterator
    aiter(async_callable, sentinel) -> async_iterator
    An async version of the iter() builtin.
    """
    lenargs = len(args)
    if lenargs != 1 and lenargs != 2:
        raise TypeError(f'aiter expected 1 or 2 arguments, got {lenargs}')
    if lenargs == 1:
        obj, = args
        if not isinstance(obj, AsyncIterable):
            raise TypeError(
                f'aiter expected an AsyncIterable, got {type(obj)}')
        async for i in obj.__aiter__():
            yield i
        return
    # lenargs == 2
    async_callable, sentinel = args
    while True:
        value = await async_callable()
        if value == sentinel:
            break
        yield value


async def anext(*args):
    """anext(async_iterator[, default])
    Return the next item from the async iterator.
    If default is given and the iterator is exhausted,
    it is returned instead of raising StopAsyncIteration.
    """
    lenargs = len(args)
    if lenargs != 1 and lenargs != 2:
        raise TypeError(f'anext expected 1 or 2 arguments, got {lenargs}')
    ait = args[0]
    if not isinstance(ait, AsyncIterator):
        raise TypeError(f'anext expected an AsyncIterable, got {type(ait)}')
    anxt = ait.__anext__
    try:
        return await anxt()
    except StopAsyncIteration:
        if lenargs == 1:
            raise
        return args[1]  # default


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

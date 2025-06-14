"""
A segment of a path.
"""

from datetime import datetime
from typing import Any, Callable, Mapping

from ..utils import parse_json_datetime

type Converter = Callable[[Any, str | None], Any]


class ParseError(Exception):
    """Exception raised on a parse error"""


def _parse_datetime(value, fmt) -> datetime | None:
    return datetime.strptime(value, fmt) if fmt else parse_json_datetime(value)


CONVERTERS: Mapping[str, Converter] = {
    'str': lambda value, fmt: value,
    'int': lambda value, fmt: int(value),
    'float': lambda value, fmt: float(value),
    'datetime': _parse_datetime,
    'path': lambda value, fmt: value,
}


class PathSegment:
    """A class representing the segment of a path"""

    def __init__(self, segment: str) -> None:
        """Create a path segment
        A path segment can be an absolute name "foo", a variable "{foo}", a
        variable and type "{foo:int}" or a variable, type, and
        format "{foo:datetime:Y-m-dTH:M:S}".

        Valid types are: int, float, str, datetime, path.
        The 'path' type catches all following segments, so '/foo/{rest:path}'
        would match '/foo/bar/grum'.
        """
        self.type: str | None = None
        self.format: str | None = None

        if segment.startswith('{') and segment.endswith('}'):
            self.name, *type_and_format = segment[1:-1].split(':', maxsplit=3)
            if len(type_and_format) == 2:
                self.type, self.format = type_and_format
            elif len(type_and_format) == 1:
                self.type, self.format = type_and_format[0], None
            else:
                self.type, self.format = 'str', None
            if self.type and self.type not in CONVERTERS:
                raise TypeError('Unknown type')
            self.is_variable = True
        elif segment.startswith('{') or segment.endswith('}'):
            raise ParseError("Invalid substitution segment")
        elif '{' in segment or '}' in segment:
            raise ParseError("Literal segment contains invalid characters")
        else:
            self.name = segment
            self.is_variable = False
            self.type = None
            self.format = None

    def match(self, value: str) -> tuple[bool, str | None, Any | None]:
        """Try to match a segment.

        :param value: The path segment to match.
        :return: A tuple of: is_match:bool, variable_name:str, value:any
        """
        if self.is_variable:
            # noinspection PyBroadException
            try:
                converter = CONVERTERS[self.type or 'str']
                value = converter(value, self.format) if self.type else value
                return True, self.name, value
            except ValueError:
                return False, None, None
        else:
            return value == self.name, None, None

    def __str__(self):
        return '<PathSegment: ' \
            f'name="{self.name}"' \
            f', is_variable={self.is_variable}' \
            f', type="{self.type}"' \
            f', format="{self.format}"' \
               '>'

    __repr__ = __str__

from typing import Optional, Tuple, Any, Callable, Mapping
from datetime import datetime
from ..types import ParseError
from ..utils import parse_json_datetime

Converter = Callable[[Any, Optional[str]], Any]

CONVERTERS: Mapping[str, Converter] = {
    'str': lambda value, fmt: value,
    'int': lambda value, fmt: int(value),
    'float': lambda value, fmt: float(value),
    'datetime': lambda value, fmt: datetime.strptime(value, fmt) if fmt else parse_json_datetime(value),
    'path': lambda value, fmt: value,
}


class PathSegment:

    def __init__(self, segment: str) -> None:
        """Create a path segment
        A path segment can be an absolute name "foo", a variable "{foo}", a variable and type "{foo:int}" or a
        variable, type, and format "{foo:datetime:Y-m-dTH:M:S}".

        Valid types are: int, float, str, datetime, path.
        The 'path' type catches all following segments, so '/foo/{rest:path}' would match '/foo/bar/grum'.
        """
        if segment.startswith('{') and segment.endswith('}'):
            self.name, *type_and_format = segment[1:-1].split(':', maxsplit=3)
            if len(type_and_format) == 2:
                self.type, self.format = type_and_format
            elif len(type_and_format) == 1:
                self.type, self.format = type_and_format[0], None
            else:
                self.type, self.format = 'str', None
            if self.type and self.type not in CONVERTERS.keys():
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

    def match(self, value: str) -> Tuple[bool, Optional[str], Optional[Any]]:
        """Try to match a segment.

        :param value: The path segment to match.
        :return: A tuple of: is_match:bool, variable_name:str, value:any
        """
        if self.is_variable:
            # noinspection PyBroadException
            try:
                converter = CONVERTERS[self.type]
                value = converter(value, self.format) if self.type else value
                return True, self.name, value
            except ValueError:
                return False, None, None
        else:
            return value == self.name, None, None

    def __str__(self):
        return '<PathSegment: ' \
                f'name="{self.name}", is_variable={self.is_variable}, type="{self.type}", format="{self.format}"' \
                '>'

    __repr__ = __str__

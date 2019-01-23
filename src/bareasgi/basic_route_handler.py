from typing import AbstractSet, Optional, Tuple, Any, Callable, Mapping
from datetime import datetime
from .types import WebHandler, RouteMatches, Scope

DEFAULT_SCHEMES = frozenset(['http', 'https'])
DEFAULT_METHODS = frozenset(['GET'])


# noinspection PyUnusedLocal
def segment_to_int(value: str, fmt: Optional[str]) -> int:
    return int(value)


# noinspection PyUnusedLocal
def segment_to_float(value: str, fmt: Optional[str]) -> float:
    return float(value)


def segment_to_datetime(value: str, fmt: Optional[str]) -> datetime:
    return datetime.strptime(value, fmt)


CONVERTERS: Mapping[str, Callable[[Any, Optional[str]], Any]] = {
    'str': lambda value, fmt: value,
    'int': lambda value, fmt: segment_to_int(value, fmt),
    'float': lambda value, fmt: segment_to_float(value, fmt),
    'datetime': lambda value, fmt: segment_to_datetime(value, fmt),
    'path': lambda value, fmt: value,
}


class ParseError(Exception):
    pass


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
            except:
                return False, None, None
        else:
            return value == self.name, None, None


class PathDefinition:
    NO_MATCH: Tuple[bool, Optional[RouteMatches]] = (False, None)


    def __init__(self, path: str) -> None:
        """Create a path definition."""
        if not path.startswith('/'):
            raise Exception('Paths must be absolute')
        # Trim off the leading '/'
        path = path[1:]

        # Handle paths that end with a '/'
        if path.endswith('/'):
            path = path[:-1]
            self.ends_with_slash = True
        else:
            self.ends_with_slash = False

        # Parse each path segment.
        self.segments = []
        for segment in path.split('/'):
            self.segments.append(PathSegment(segment))


    def match(self, path: str) -> Tuple[bool, Optional[RouteMatches]]:
        """Try to match the given path with this path definition

        :param path: The path to match.
        :return: A tuple of: is_match:bool, matches:dict.
        """
        if not path.startswith('/'):
            raise Exception('Paths must be absolute')

        # Handle trailing slash
        if path[1:].endswith('/'):
            if not self.ends_with_slash:
                return self.NO_MATCH
            path = path[:-1]
        elif self.ends_with_slash:
            return self.NO_MATCH

        parts = path[1:].split('/')

        # Must have at least the same number of segments.
        if len(parts) < len(self.segments):
            return self.NO_MATCH

        # Keep the matches we find.
        matches = {}

        # A path with more segments is allowed if the last segment is a variable of type 'path'.
        if len(parts) > len(self.segments):
            last_segment = self.segments[-1]
            if last_segment.type != 'path':
                return self.NO_MATCH
            matches[last_segment.name] = parts[len(self.segments):]
            parts = parts[:len(self.segments)]

        # Now the path parts and segments are the same length we can check them.
        for part, segment in zip(parts, self.segments):
            is_match, name, value = segment.match(part)
            if not is_match:
                return self.NO_MATCH
            if name:
                matches[name] = value

        return True, matches


class BasicRouteHandler:

    def __init__(self) -> None:
        self._routes = {}


    def add(
            self,
            handler: WebHandler,
            path: str,
            methods: AbstractSet[str] = DEFAULT_METHODS,
            schemes: AbstractSet[str] = DEFAULT_SCHEMES
    ) -> None:
        """Add a route"""
        for scheme in schemes:
            method_dict = self._routes.setdefault(scheme, {})
            for method in methods:
                path_definition_list = method_dict.setdefault(method, [])
                path_definition_list.append((PathDefinition(path), handler))


    def match(self, scheme: str, method: str, path: str) -> Tuple[Optional[WebHandler], Optional[RouteMatches]]:
        """Find a match for the scheme, method, and path.

        :param scheme: The schemes: e.g. 'http', 'https', 'ws', 'wss', etc.
        :param method: The method: e.g. 'GET', 'POST', etc.
        :param path: The path: e.g. '/foo/bar/{name:str}'.
        :return: A tuple of handler:callable, matches:dict.
        """
        method_dict = self._routes.get(scheme)
        if method_dict:
            path_definition_list = method_dict.get(method)
            if path_definition_list:
                for path_definition, handler in path_definition_list:
                    is_match, matches = path_definition.match(path)
                    if is_match:
                        return handler, matches
        return None, None


    def __call__(self, scope: Scope) -> Tuple[Optional[WebHandler], Optional[RouteMatches]]:
        return self.match(scope['scheme'], scope['method'], scope['path'])

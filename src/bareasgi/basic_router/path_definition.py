from typing import Optional, Tuple
from ..types import RouteMatches
from .path_segment import PathSegment


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
        if path[1:].endswith('/') and self.segments[-1].type != 'path':
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
            index = len(self.segments) - 1
            matches[last_segment.name] = '/'.join(parts[index:])
            parts = parts[:index]

        # Now the path parts and segments are the same length we can check them.
        for part, segment in zip(parts, self.segments):
            is_match, name, value = segment.match(part)
            if not is_match:
                return self.NO_MATCH
            if name:
                matches[name] = value

        return True, matches

    def __str__(self):
        return f'<PathDefinition: segments={self.segments}, ends_with_slash={self.ends_with_slash}>'

    __repr__ = __str__

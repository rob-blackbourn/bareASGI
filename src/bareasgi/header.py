import collections
from typing import List, Optional, Mapping, MutableMapping
from .types import Header


def index(name: bytes, headers: List[Header]) -> int:
    """Find the index of the header in the list.

    :param name: The header name.
    :param headers: The headers to search.
    :return: The index of the header or -1 if not found.
    """
    return next((i for i, (k, v) in enumerate(headers) if k == name), -1)


def find(name: bytes, headers: List[Header], default: Optional[bytes] = None) -> Optional[bytes]:
    """Find the value of a header, or return a default value.

    :param name: The name of the header.
    :param headers: The headers to search.
    :param default: An optional default value, otherwise None.
    :return: The value of the header if found, otherwise the default value.
    """
    return next((v for k, v in headers if k == name), default)


def find_all(name: bytes, headers: List[Header]) -> List[bytes]:
    """Find all the values for a given header.

    :param name: The name of the header.
    :param headers: The headers to search.
    :return: A list of the header values which may be empty if there were none found.
    """
    return [v for k, v in headers if k == name]


def upsert(name: bytes, value: bytes, headers: List[Header]) -> None:
    """If the header exists overwrite the value, otherwise append a new value.

    :param name: The header name.
    :param value: The header value.
    :param headers: The headers.
    """
    for i in range(len(headers)):
        if headers[i][0] == name:
            headers[i] = (name, value)
            return
    headers.append((name, value))


def to_dict(headers: List[Header]) -> MutableMapping[bytes, List[bytes]]:
    """Convert a list of headers into a dictionary where the key is the header name and the value is a list of the
    values of the headers for that name

    :param headers: A list of headers.
    :return: A dictionary where the key is the header name and the value is a list of the values of the headers for that
        name
    """
    items: MutableMapping[bytes, List[bytes]] = collections.defaultdict(list)
    for name, value in headers:
        items[name].append(value)
    return items


def parse_quality(value: bytes) -> Optional[float]:
    """Parse a quality attribute of the form 'q=0.5'

    :param value: The attribute value
    :return: The value as a float or None if there was no value.
    :raises: ValueError if there was a 'q' qualifier, but no value.
    """
    if value == b'':
        return None
    k, v = value.split(b'=')
    if k != b'q':
        raise ValueError('expected "q"')
    return float(v)


def accept_encoding(headers: List[Header], *, add_identity: bool = False) -> Optional[Mapping[bytes, float]]:
    """Extracts the accept encoding header if it exists into a mapping of the encoding
    and the quality value which defaults to 1.0 if missing.

    :param headers: The headers to search.
    :param add_identity: If True ensures the 'identity' encoding is included.
    :return: A mapping of the encodings and qualities.
    """
    value = find(b'accept-encoding', headers)
    if value is None:
        return None

    encodings = {
        first: parse_quality(rest) or 1.0
        for first, sep, rest in [x.partition(b';') for x in value.split(b', ')]
    }

    if add_identity and b'identity' not in encodings:
        encodings[b'identity'] = 1.0

    return encodings


def content_encoding(headers: List[Header], *, add_identity: bool = False) -> Optional[List[bytes]]:
    """Returns the content encodings in a list or None if they were not specified.

    :param headers: The headers.
    :param add_identity: If True ensures the 'identity' encoding is included.
    :return: The list of content encodings or None is absent.
    """
    value = find(b'content-encoding', headers)
    if value is None:
        return None

    encodings = value.split(b', ')

    if add_identity and b'identity' not in encodings:
        encodings.append(b'identity')

    return encodings


def content_length(headers: List[Header]) -> Optional[int]:
    """Returns the content length as an integer if specified, otherwise None.

    :param headers: The headers.
    :return: The length as an integer or None is absent.
    """
    value = find(b'content-length', headers)
    if value is None:
        return None

    return int(value)


def cookie(headers: List[Header]) -> Mapping[bytes, bytes]:
    """Returns the cookies as a name-value mapping.

    :param headers: The headers.
    :return: The cookies as a name-value mapping.
    """
    cookies: MutableMapping[bytes, bytes] = dict()
    for header in find_all(b'cookie', headers):
        for item in header.split(b'; '):
            first, sep, rest = item.partition(b'=')
            if first == b'':
                continue
            cookies[first] = rest[:-1] if rest.endswith(b';') else rest
    return cookies


def vary(headers: List[Header]) -> Optional[List[bytes]]:
    """Returns the vary header value as a list of headers.

    :param headers: The headers.
    :return: A list of the vary headers.
    """
    value = find(b'vary', headers)
    return value.split(b', ') if value is not None else None

from typing import List, Optional, Mapping
from .types import Header


def index(name: bytes, headers: List[Header]) -> int:
    """Find the index of the header in the list.

    :param name: The header name.
    :param headers: The headers
    :return: The index of the header or -1 if not found.
    """
    return next((i for i, (k, v) in enumerate(headers) if k == name), -1)


def find(name: bytes, headers: List[Header], default: Optional[bytes] = None) -> Optional[bytes]:
    return next((v for k, v in headers if k == name), default)


def find_all(name: bytes, headers: List[Header]) -> List[bytes]:
    return [v for k, v in headers if k == name]


def parse_quality(value: bytes) -> Optional[float]:
    if value == b'':
        return None
    k, v = value.split(b'=')
    if k != b'q':
        raise ValueError('expected "q"')
    return float(v)


def accept_encoding(headers: List[Header], *, add_identity: bool = False) -> Optional[Mapping[bytes, float]]:
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
    value = find(b'content-encoding', headers)
    if value is None:
        return None

    encodings = value.split(b', ')

    if add_identity and b'identity' not in encodings:
        encodings.append(b'identity')

    return encodings


def content_length(headers: List[Header]) -> Optional[int]:
    value = find(b'content-length', headers)
    if value is None:
        return None

    return int(value)

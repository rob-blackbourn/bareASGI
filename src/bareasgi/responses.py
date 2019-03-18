import json
from typing import List, Union, Mapping, Any
from .types import Header, HttpResponse
from .streaming import bytes_writer


def bytes_response(
        status: int,
        headers: List[Header],
        buf: bytes,
        content_type: bytes
) -> HttpResponse:
    headers.append((b'content-type', content_type))
    headers.append((b'content-length', str(len(buf)).encode('ascii')))
    return status, headers, bytes_writer(buf)


def text_response(
        status: int,
        headers: List[Header],
        text: str,
        encoding: str = 'utf-8',
        content_type: bytes = b'text/plain'
) -> HttpResponse:
    return bytes_response(status, headers, text.encode(encoding), content_type)


def json_response(
        status: int,
        headers: List[Header],
        obj: Union[List[Any], Mapping[str, Any]],
        content_type: bytes = b'application/json',
        dumps=json.dumps
) -> HttpResponse:
    return text_response(status, headers, dumps(obj), 'utf-8', content_type)

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
    """
    A helper function to create a bytes response.

    :param status: The HTTP status code.
    :param headers: The HTTP headers.
    :param buf: The date to send.
    :param content_type: The content type of the data.
    :return: The HTTP response.
    """
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
    """
    A helper function to create a text response.

    :param status: The HTTP status code.
    :param headers: The HTTP headers.
    :param text: The text to send.
    :param encoding: The text encoding (defauults to utf-8).
    :param content_type: The content type (defaults to text/plain).
    :return: The HTTP response.
    """
    return bytes_response(status, headers, text.encode(encoding), content_type)


def json_response(
        status: int,
        headers: List[Header],
        obj: Union[List[Any], Mapping[str, Any]],
        content_type: bytes = b'application/json',
        dumps=json.dumps
) -> HttpResponse:
    """
    A helper function to send a json repsonse.

    :param status: The HTTP status code.
    :param headers: The HTTP headers.
    :param obj: The object to send as JSON.
    :param content_type: The content type (defaults to application/json).
    :param dumps: The function to use to turn the object into JSON (defaults to json.dumps)
    :return: The HTTP response.
    """
    return text_response(status, headers, dumps(obj), 'utf-8', content_type)

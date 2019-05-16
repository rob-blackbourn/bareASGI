from datetime import datetime, timedelta, timezone
from typing import Optional, Union

_GMT = timezone(timedelta(), 'GMT')


def make_cookie(
        key: bytes,
        value: bytes,
        *,
        expires: Optional[Union[datetime, timedelta]] = None,
        path: Optional[bytes] = None,
        domain: Optional[bytes] = None,
        secure: bool = False,
        http_only: bool = False,
        same_site: Optional[bool] = None
) -> bytes:
    if key.startswith(b'__Secure-') or key.startswith(b'__Host-') and not secure:
        raise RuntimeError('Keys starting __Secure- or __Host- require the secure directive')

    cookie = key + b'=' + value

    if expires is not None:
        if isinstance(expires, datetime):
            cookie += b'; Expires=' + expires.astimezone(_GMT).strftime('%a, %d %b %Y %H:%M:%S %Z').encode()
        else:
            cookie += b'; Max-Age=' + str(int(expires.total_seconds())).encode()

    if domain is not None:
        cookie += b'; Domain=' + domain

    if path is not None:
        cookie += b'; Path=' + path

    if secure:
        cookie += b'; Secure'

    if http_only:
        cookie += b'; HttpOnly'

    if same_site is not None:
        cookie += b'; SameSite=' + b'Strict' if same_site else b'Lax'

    return cookie


def make_expired_cookie(key: str, path: bytes = b'/') -> bytes:
    return make_cookie(key, b'', expires=timedelta(seconds=0), path=path)

from datetime import datetime, timedelta, timezone
import re
from typing import Optional, Union, Mapping, MutableMapping, Any, List

# Date: <day-name>, <day> <month> <year> <hour>:<minute>:<second> GMT
DATE_PATTERN = re.compile(
    r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun), (\d{2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4}) (\d{2}):(\d{2}):(\d{2}) GMT$'
)
DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTH_NAMES = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def parse_date(value: str) -> datetime:
    matches = DATE_PATTERN.match(value)
    day_of_week, day, month, year, hour, minute, second = matches.groups()
    result = datetime(
        int(year),
        1 + MONTH_NAMES.index(month),
        int(day),
        int(hour),
        int(minute),
        int(second),
        tzinfo=timezone.utc
    )
    return result


def format_date(value: datetime) -> str:
    year, mon, mday, hour, min, sec, wday, yday, isdst = value.utctimetuple()
    return f"{DAY_NAMES[wday]}, {mday:02d} {MONTH_NAMES[mon - 1]} {year:04d} {hour:02d}:{min:02d}:{sec:02d} GMT"


def encode_set_cookie(
        name: bytes,
        value: bytes,
        *,
        expires: Optional[datetime] = None,
        max_age: Optional[Union[int, timedelta]] = None,
        path: Optional[bytes] = None,
        domain: Optional[bytes] = None,
        secure: bool = False,
        http_only: bool = False,
        same_site: Optional[bool] = None
) -> bytes:
    if name.startswith(b'__Secure-') or name.startswith(b'__Host-') and not secure:
        raise RuntimeError('Keys starting __Secure- or __Host- require the secure directive')

    set_cookie = name + b'=' + value

    if expires is not None:
        set_cookie += b'; Expires=' + format_date(expires).encode()

    if max_age is not None:
        if isinstance(max_age, timedelta):
            set_cookie += b'; Max-Age=' + str(int(max_age.total_seconds())).encode()
        else:
            set_cookie += b'; Max-Age=' + str(int(max_age)).encode()

    if domain is not None:
        set_cookie += b'; Domain=' + domain

    if path is not None:
        set_cookie += b'; Path=' + path

    if secure:
        set_cookie += b'; Secure'

    if http_only:
        set_cookie += b'; HttpOnly'

    if same_site is not None:
        set_cookie += b'; SameSite=' + b'Strict' if same_site else b'Lax'

    return set_cookie


def decode_set_cookie(set_cookie: bytes) -> Mapping[str, Any]:
    i = iter(set_cookie.split(b';'))
    key, value = next(i).split(b'=', maxsplit=2)
    result = {'name': key, 'value': value}
    for item in i:
        key, _, value = item.partition(b'=')
        key = key.lower().strip().decode('ascii')
        if key == 'secure':
            result['secure'] = True
        elif key == 'httponly':
            result['http_only'] = True
        elif key == 'expires':
            result['expires'] = parse_date(value.decode('ascii'))
        elif key == 'max-age':
            result['max_age'] = timedelta(seconds=int(value))
        elif key == 'samesite':
            result['same_site'] = value.lower() == b'strict'
        else:
            result[key] = value
    return result


def encode_cookies(cookies: Mapping[bytes, List[bytes]]) -> bytes:
    return b'; '.join(name + b'=' + value for name, values in cookies.items() for value in values)


def decode_cookies(cookies: bytes) -> Mapping[bytes, List[bytes]]:
    result: MutableMapping[bytes, List[bytes]] = dict()
    for morsel in cookies.rstrip(b'; ').split(b'; '):
        name, _, value = morsel.partition(b'=')
        result.setdefault(name, []).append(value)
    return result


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
    return encode_set_cookie(
        key,
        value,
        expires=expires if isinstance(expires, datetime) else None,
        max_age=expires if isinstance(expires, (int, timedelta)) else None,
        path=path,
        domain=domain,
        secure=secure,
        http_only=http_only,
        same_site=same_site
    )


def make_expired_cookie(key: bytes, path: bytes = b'/') -> bytes:
    return make_cookie(key, b'', expires=timedelta(seconds=0), path=path)

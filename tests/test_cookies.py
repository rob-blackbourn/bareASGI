from datetime import datetime, timedelta, timezone
from bareasgi.cookies import make_cookie


def test_make_cookie():
    assert make_cookie(b'foo', b'bar') == b'foo=bar'
    assert make_cookie(
        b'sessionid', b'38afes7a8', http_only=True, path=b'/'
    ) == b'sessionid=38afes7a8; Path=/; HttpOnly'
    assert make_cookie(
        b'id', b'a3fWa', expires=datetime(2015, 10, 21, 7, 28, 0, tzinfo=timezone.utc), secure=True, http_only=True
    ) == b'id=a3fWa; Expires=Wed, 21 Oct 2015 07:28:00 GMT; Secure; HttpOnly'
    assert make_cookie(
        b'qwerty',
        b'219ffwef9w0f',
        domain=b'somecompany.co.uk',
        path=b'/',
        expires=datetime(2019, 8, 30, 0, 0, 0, tzinfo=timezone.utc)
    ) == b'qwerty=219ffwef9w0f; Expires=Fri, 30 Aug 2019 00:00:00 GMT; Domain=somecompany.co.uk; Path=/'

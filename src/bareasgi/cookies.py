import http.cookies


def make_cookie(
        key: str,
        value: str = "",
        max_age: int = None,
        expires: int = None,
        path: str = "/",
        domain: str = None,
        secure: bool = False,
        httponly: bool = False,
) -> bytes:
    cookie = http.cookies.SimpleCookie()
    cookie[key] = value
    if max_age is not None:
        cookie[key]["max-age"] = max_age  # type: ignore
    if expires is not None:
        cookie[key]["expires"] = expires  # type: ignore
    if path is not None:
        cookie[key]["path"] = path
    if domain is not None:
        cookie[key]["domain"] = domain
    if secure:
        cookie[key]["secure"] = True  # type: ignore
    if httponly:
        cookie[key]["httponly"] = True  # type: ignore
    cookie_val = cookie.output(header="").strip()
    return cookie_val.encode('ascii')


def make_expired_cookie(key: str, path: str = "/", domain: str = None) -> bytes:
    return make_cookie(key, expires=0, max_age=0, path=path, domain=domain)

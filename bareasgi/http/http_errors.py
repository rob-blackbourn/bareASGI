"""Types for bareASGI and bareClient"""


class HttpInternalError(Exception):
    """Exception raised for an internal error"""


class HttpDisconnectError(Exception):
    """Exception raise on HTTP disconnect"""

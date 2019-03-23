from typing import List, Optional, AsyncIterable
import logging
from .types import (
    HttpInternalError,
    HttpDisconnectError,
    Scope,
    Info,
    Send,
    Receive,
    Header,
    HttpRouter,
    Context,
    HttpMiddlewareCallback
)
from .middleware import mw
from .utils import anext

logger = logging.getLogger(__name__)


async def _send_response(
        send: Send,
        status: int,
        headers: Optional[List[Header]] = None,
        body: Optional[AsyncIterable[bytes]] = None
) -> None:
    # Create and send the start response.
    response_start = {'type': 'http.response.start', 'status': status}
    if headers:
        response_start['headers'] = headers
    logger.debug(f'Sending "http.response.start" with status {status}', extra=response_start)
    await send(response_start)

    # Create and send the response body.
    response_body = {'type': 'http.response.body'}

    # If we don't get a body, just send the basic response.
    try:
        buf = await anext(body) if body else None
    except StopAsyncIteration:
        buf = None
    if buf is None:
        logger.debug(f'Sending "http.response.body" with empty body', extra=response_body)
        await send(response_body)
        return

    # Continue to get and send the body until exhausted.
    while buf is not None:
        response_body['body'] = buf
        try:
            buf = await anext(body)
            response_body['more_body'] = True
        except StopAsyncIteration:
            buf = None
            response_body['more_body'] = False
        logger.debug(f'Sending "http.response.body" with more_body="{response_body["more_body"]}', extra=response_body)
        if len(response_body['body']) > 0:
            await send(response_body)


async def _body_iterator(receive: Receive, body: bytes, more_body: bool) -> AsyncIterable[bytes]:
    yield body
    while more_body:
        request = await receive()
        request_type = request['type']
        logger.debug(f'Received {request_type}', extra=request)

        if request_type == 'http.request':
            body, more_body = request.get('body', b''), request.get('more_body', False)
            yield body
        elif request_type == 'http.disconnect':
            raise HttpDisconnectError
        else:
            logger.error(f'Failed to understand request type "{request_type}', extra=request)
            raise HttpInternalError


class HttpInstance:

    def __init__(self, scope: Scope, context: Context, info: Optional[Info] = None) -> None:
        self.scope = scope
        self.info = info or {}
        # Find the route.
        route_handler: HttpRouter = context['router']
        self.request_callback, self.matches = route_handler(scope)
        # Apply middleware.
        middleware: Optional[List[HttpMiddlewareCallback]] = context['middlewares']
        if middleware:
            self.request_callback = mw(*middleware, handler=self.request_callback)


    async def __call__(self, receive: Receive, send: Send) -> None:

        request = await receive()
        request_type = request['type']
        logger.debug(f'Received request {request_type}', extra=request)

        if request_type == 'http.request':
            response = await self.request_callback(
                self.scope,
                self.info,
                self.matches,
                _body_iterator(receive, request.get('body', b''), request.get('more_body', False)),
            )
            await _send_response(send, *response)

        elif request_type == 'http.disconnect':
            # TODO: What to do here?
            raise HttpDisconnectError

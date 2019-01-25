from typing import List, Optional, AsyncIterable
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
    await send(response_start)

    # Create and send the response body.
    response_body = {'type': 'http.response.body'}

    # If we don't get a body, just send the basic response.
    buf = await anext(body) if body else None
    if not buf:
        await send(response_body)
        return

    # Continue to get and send the body until exhausted.
    while buf:
        response_body['body'] = buf
        try:
            buf = await anext(body)
            response_body['more_body'] = True
        except StopAsyncIteration:
            buf = None
            response_body['more_body'] = False
        await send(response_body)


async def _body_iterator(receive: Receive, body: bytes, more_body: bool) -> AsyncIterable[bytes]:
    yield body
    while more_body:
        message = await receive()
        if message['type'] == 'http.request':
            body, more_body = message.get('body', b''), message.get('more_body', False)
            yield body
        elif message['type'] == 'http.disconnect':
            raise HttpDisconnectError
        else:
            # TODO: What to do here?
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

        if request['type'] == 'http.request':
            response = await self.request_callback(
                self.scope,
                self.info,
                self.matches,
                _body_iterator(receive, request.get('body', b''), request.get('more_body', False)),
            )
            await _send_response(send, *response)

        elif request['type'] == 'http.disconnect':
            # TODO: What to do here?
            raise HttpDisconnectError

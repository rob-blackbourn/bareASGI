from typing import List, Optional, AsyncIterable
from .types import (
    Scope,
    Info,
    Send,
    Receive,
    Header,
    HttpRouter,
    Context,
    HttpResponse,
    HttpMiddlewareCallback
)
from .middleware import mw
from .streams import text_writer
from .utils import anext


async def _send_response(
        send: Send,
        status: int,
        headers: Optional[List[Header]] = None,
        body: Optional[AsyncIterable[bytes]] = None
) -> None:
    response_start = {'type': 'http.response.start', 'status': status}
    if headers:
        response_start['headers'] = headers
    await send(response_start)

    response_body = {'type': 'http.response.body'}

    buf = await anext(body) if body else None
    if not buf:
        await send(response_body)
        return

    while buf:
        response_body['body'] = buf
        try:
            buf = await anext(body)
            response_body['more_body'] = True
        except StopAsyncIteration:
            buf = None
            response_body['more_body'] = False
        await send(response_body)


async def _make_body_iterator(receive: Receive, body: bytes, more_body: bool) -> AsyncIterable[bytes]:
    yield body
    while more_body:
        message = await receive()
        body, more_body = message.get('body', b''), message.get('more_body', False)
        yield body


class HttpInstance:

    def __init__(self, scope: Scope, context: Context, info: Optional[Info] = None) -> None:
        self.scope = scope
        self.info = info or {}
        route_handler: HttpRouter = context['router']
        self.request_handler, self.matches = route_handler(scope)
        middleware: Optional[List[HttpMiddlewareCallback]] = context['middlewares']
        if middleware:
            self.request_handler = mw(*middleware, handler=self.request_handler)
        self.not_found_response: HttpResponse = context['404']


    async def __call__(self, receive: Receive, send: Send) -> None:

        request = await receive()

        if request['type'] == 'http.request':
            if self.request_handler:
                response = await self.request_handler(
                    self.scope,
                    self.info,
                    self.matches,
                    _make_body_iterator(receive, request.get('body', b''), request.get('more_body', False)),
                )
                await _send_response(send, *response)
            else:
                await _send_response(send, *self.not_found_response)

        elif request['type'] == 'http.disconnect':
            pass

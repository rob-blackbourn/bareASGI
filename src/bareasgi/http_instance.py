from typing import List, Optional, AsyncIterable
from .types import (
    Scope,
    Info,
    Send,
    Receive,
    Header,
    HttpRouteHandler
)
from .streams import text_writer
from .utils import anext


class HttpInstance:

    def __init__(self, scope: Scope, route_handler: HttpRouteHandler, info: Optional[Info] = None) -> None:
        self.scope = scope
        self.info = info or {}
        self.request_handler, self.matches = route_handler(scope)


    async def __call__(self, receive: Receive, send: Send) -> None:

        # A closure to capture 'receive'.
        async def response(
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


        async def request_iter(body: bytes, more_body: bool) -> AsyncIterable[bytes]:
            yield body
            while more_body:
                message = await receive()
                body, more_body = message.get('body', b''), message.get('more_body', False)
                yield body


        # Fetch the http message
        request = await receive()

        if request['type'] == 'http.request':
            if self.request_handler:
                await self.request_handler(
                    self.scope,
                    self.info,
                    self.matches,
                    request_iter(request.get('body', b''), request.get('more_body', False)),
                    response
                )
            else:
                await response(404, [(b'content-type', b'text/plain')], text_writer('not Found'))

        elif request['type'] == 'http.disconnect':
            pass

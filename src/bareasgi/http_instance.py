from typing import List, Optional, AsyncIterable, AsyncGenerator
from .types import (
    Scope,
    Info,
    Send,
    Receive,
    Header,
    HttpRouteHandler,
    Content
)
import codecs
from .utils import anext


async def bytes_reader(content: Content) -> bytes:
    buf = b''
    async for b in content:
        buf += b
    return buf


async def text_reader(content: Content, encoding: str = 'utf-8') -> str:
    codec_info: codecs.CodecInfo = codecs.lookup(encoding)
    decoder = codec_info.incrementaldecoder()
    text = ''
    async for b in content:
        text += decoder.decode(b)
    return text


async def bytes_writer(buf: bytes) -> AsyncGenerator[bytes, None]:
    yield buf


async def text_writer(text: str, encoding: str = 'utf-8') -> AsyncGenerator[bytes, None]:
    yield text.encode(encoding=encoding)


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
            await self.request_handler(
                self.scope,
                self.info,
                self.matches,
                request_iter(request.get('body', b''), request.get('more_body', False)),
                response
            )
        elif request['type'] == 'http.disconnect':
            pass

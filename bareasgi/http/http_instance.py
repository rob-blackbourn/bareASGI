"""The http instance"""

import asyncio
from asyncio import Queue
import logging
from typing import (
    Any,
    AsyncIterable,
    Dict,
    Iterable,
    List,
    Set,
    Tuple,
    cast
)

from asgi_typing import (
    HTTPResponseBodyEvent,
    HTTPScope,
    ASGIHTTPReceiveCallable,
    ASGIHTTPSendCallable,
    HTTPRequestEvent,
    HTTPResponseStartEvent,
    HTTPServerPushEvent
)

from ..utils import NullIter

from .http_callbacks import HttpMiddlewareCallback
from .http_errors import HttpInternalError, HttpDisconnectError
from .http_request import HttpRequest
from .http_response import HttpResponse, PushResponse
from .http_router import HttpRouter
from .http_middleware import make_middleware_chain

LOGGER = logging.getLogger(__name__)


class BodyIterator:
    """Iterate over the body content"""

    def __init__(
            self,
            receive: ASGIHTTPReceiveCallable,
            body: bytes,
            more_body: bool
    ) -> None:
        """Initialise the body iterator

        Args:
            receive (Receive): The receive callable
            body (bytes): The initial body
            more_body (bool): Signifies if there is additional content to come.
        """
        self._receive = receive
        self._queue: Queue = Queue()
        self._queue.put_nowait(body)
        self._more_body = more_body

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._queue.empty():
            body = await self._queue.get()
            return body

        if not self._more_body:
            raise StopAsyncIteration

        return await self._read()

    async def _read(self) -> bytes:
        event = await self._receive()
        LOGGER.debug('Received event type "%s".', event['type'])

        if event['type'] == 'http.disconnect':
            raise HttpDisconnectError

        if event['type'] != 'http.request':
            LOGGER.error(
                'Failed to understand event type "%s".', event['type'])
            raise HttpInternalError

        request_event = cast(HTTPRequestEvent, event)
        body = request_event.get('body', b'')
        self._more_body = request_event.get('more_body', False)
        return body

    async def flush(self) -> None:
        """Flush all remaining http.request messages"""
        while self._more_body:
            await self._queue.put(await self._read())


class HttpInstance:
    """An HTTP instance services an HTTP request."""

    def __init__(
            self,
            scope: HTTPScope,
            router: HttpRouter,
            middleware: Iterable[HttpMiddlewareCallback],
            info: Dict[str, Any]
    ) -> None:
        self.scope = scope
        self.info = info

        # Find the route.
        self.handler, self.matches = router.resolve(
            scope['method'],
            scope['path']
        )

        # Assemble any middleware.
        if middleware:
            self.handler = make_middleware_chain(
                *middleware,
                handler=self.handler
            )

    async def process(
            self,
            receive: ASGIHTTPReceiveCallable,
            send: ASGIHTTPSendCallable
    ) -> None:

        LOGGER.debug('Start handling request.')

        try:
            request_event = await self._receive_request(receive)

            response = await self._handle_request(receive, request_event)

            await self._send_response(receive, send, response)

        except asyncio.CancelledError:
            pass

    async def _receive_request(
            self,
            receive: ASGIHTTPReceiveCallable,
    ) -> HTTPRequestEvent:
        event = await receive()
        if event['type'] != 'http.request':
            raise HttpInternalError('Expected http.request')
        return cast(HTTPRequestEvent, event)

    async def _handle_request(
            self,
            receive: ASGIHTTPReceiveCallable,
            request_event: HTTPRequestEvent
    ) -> HttpResponse:
        body = BodyIterator(
            receive,
            request_event.get('body', b''),
            request_event.get('more_body', False)
        )
        request = HttpRequest(
            self.scope,
            self.info,
            {},
            self.matches,
            body
        )

        response = await self.handler(request)

        # Typically the request handler has already processed the request
        # body, but we flush all the "http.request" messages so we can catch
        # the final "http.disconnect".
        await body.flush()

        return response

    async def _send_response(
            self,
            receive: ASGIHTTPReceiveCallable,
            send: ASGIHTTPSendCallable,
            response: HttpResponse
    ) -> None:
        send_task = asyncio.create_task(
            self._send_response_events(send, response)
        )
        receive_task = asyncio.create_task(receive())
        pending: Set[asyncio.Future] = {send_task, receive_task}

        is_connected = True

        while is_connected:

            done, pending = await asyncio.wait(
                pending,
                return_when=asyncio.FIRST_COMPLETED
            )

            if receive_task in done:
                event = receive_task.result()
                LOGGER.debug('Received event type "%s".', event)

                # Cancel pending tasks.
                for task in pending:
                    try:
                        task.cancel()
                        await task
                    except:  # pylint: disable=bare-except
                        pass

                # Check for abnormal disconnection.
                if event['type'] != 'http.disconnect':
                    raise HttpInternalError(
                        f'Unexpected request type "{event["type"]}"'
                    )

                LOGGER.debug('Disconnecting.')

                is_connected = False
            elif send_task in done:
                # Fetch result to trigger possible exceptions
                send_task.result()

        LOGGER.debug('Finish handling request.')

    async def _send_response_events(
            self,
            send: ASGIHTTPSendCallable,
            response: HttpResponse
    ) -> None:
        await self._send_response_start_event(
            send,
            response.status,
            response.headers or []
        )

        if response.pushes is not None and self._is_http_push_supported:
            await self._send_response_push_event(send, response.pushes)

        await self._send_response_body_event(send, response.body or NullIter())

    async def _send_response_start_event(
            self,
            send: ASGIHTTPSendCallable,
            status: int,
            headers: List[Tuple[bytes, bytes]]
    ) -> None:
        response_start_event: HTTPResponseStartEvent = {
            'type': 'http.response.start',
            'status': status,
            'headers': headers
        }

        LOGGER.debug('Sending "http.response.start" with status "%s".', status)
        await send(response_start_event)

    async def _send_response_push_event(
            self,
            send: ASGIHTTPSendCallable,
            pushes: Iterable[PushResponse]
    ) -> None:
        for push_path, push_headers in pushes:
            LOGGER.debug(
                'Sending "http.response.push" for path "%s".',
                push_path
            )
            server_push_event: HTTPServerPushEvent = {
                'type': 'http.response.push',
                'path': push_path,
                'headers': push_headers
            }
            await send(server_push_event)

    async def _send_response_body_event(
            self,
            send: ASGIHTTPSendCallable,
            body: AsyncIterable[bytes]
    ) -> None:
        body_iter = body.__aiter__()
        is_first_time = True
        more_body = True
        buf = b''
        while more_body:
            prev = buf
            try:
                # Try to get more body
                buf = await body_iter.__anext__()
            except StopAsyncIteration:
                # The previous buf was the last
                more_body = False

            if is_first_time and more_body:
                is_first_time = False
                continue

            response_body_event: HTTPResponseBodyEvent = {
                'type': 'http.response.body',
                'body': prev,
                'more_body': more_body
            }
            LOGGER.debug(
                'Sending "http.response.body" with more body "%s".',
                more_body
            )
            await send(response_body_event)

    @property
    def _is_http_push_supported(self) -> bool:
        extensions = self.scope.get('extensions', {})
        return (
            self.scope['http_version'] in ('2', '2.0') and
            extensions is not None and
            'http.response.push' in extensions
        )

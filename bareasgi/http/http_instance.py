"""
HTTP Instance
"""

import asyncio
from asyncio import Queue
import logging
from typing import (
    Any,
    Dict,
    Iterable,
    Set,
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

from ..utils import anext

from .http_callbacks import HttpMiddlewareCallback
from .http_errors import HttpInternalError, HttpDisconnectError, HttpError
from .http_request import HttpRequest
from .http_response import HttpResponse
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
        LOGGER.debug(
            'Received "%s"',
            event['type'],
            extra=cast(Dict[str, Any], event)
        )

        if event['type'] == 'http.disconnect':
            raise HttpDisconnectError

        if event['type'] != 'http.request':
            LOGGER.error(
                'Failed to understand request type "%s"',
                event['type'],
                extra=cast(Dict[str, Any], event)
            )
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
        if self.handler is None:
            raise ValueError(
                f"Handler not found for {scope['method']} {scope['path']}"
            )

        # Assemble any middleware.
        if middleware:
            self.handler = make_middleware_chain(
                *middleware,
                handler=self.handler
            )

    @property
    def _is_http_2(self) -> bool:
        return self.scope['http_version'] in ('2', '2.0')

    @property
    def _is_http_push_supported(self) -> bool:
        extensions = self.scope.get('extensions', {})
        return (
            self._is_http_2 and
            extensions is not None and
            'http.response.push' in extensions
        )

    async def _send_response(
            self,
            send: ASGIHTTPSendCallable,
            response: HttpResponse
    ) -> None:
        # Create and send the start response.
        response_start_event: HTTPResponseStartEvent = {
            'type': 'http.response.start',
            'status': response.status,
            'headers': response.headers or []
        }

        LOGGER.debug(
            'Sending "http.response.start" with status %s',
            response.status,
            extra=cast(Dict[str, Any], response_start_event)
        )
        await send(response_start_event)

        if response.pushes is not None and self._is_http_push_supported:
            for push_path, push_headers in response.pushes:
                LOGGER.debug(
                    'sending "http.response.push" for path "%s"',
                    push_path
                )
                server_push_event: HTTPServerPushEvent = {
                    'type': 'http.response.push',
                    'path': push_path,
                    'headers': push_headers
                }
                await send(server_push_event)

        # Create and send the response body.

        # If we don't get a body, just send the basic response.
        try:
            buf = await anext(response.body) if response.body else None
        except StopAsyncIteration:
            buf = None
        if buf is None:
            response_body_event: HTTPResponseBodyEvent = {
                'type': 'http.response.body',
                'body': b'',
                'more_body': False
            }
            LOGGER.debug(
                'Sending "http.response.body" with empty body',
                extra=cast(Dict[str, Any], response_body_event)
            )
            await send(response_body_event)
            return

        # Continue to get and send the body until exhausted.
        while buf is not None:
            body = buf
            try:
                buf = await anext(response.body)
                more_body = True
            except StopAsyncIteration:
                buf = None
                more_body = False
            if body:
                response_body_event = {
                    'type': 'http.response.body',
                    'body': body,
                    'more_body': more_body
                }
                LOGGER.debug(
                    'Sending "http.response.body" with more_body="%s',
                    more_body,
                    extra=cast(Dict[str, Any], response_body_event)
                )
                await send(response_body_event)

    async def __call__(
            self,
            receive: ASGIHTTPReceiveCallable,
            send: ASGIHTTPSendCallable
    ) -> None:

        LOGGER.debug('start handling request')

        # The first step is to receive the ASGI request.
        try:
            event = await receive()
            if event['type'] != 'http.request':
                raise HttpInternalError('Expected http.request')
        except asyncio.CancelledError:
            # At this stage we only handle a cancellation. All
            # other errors fall through to the ASGI server.
            return

        # The next step is to call the handler.
        body = BodyIterator(
            receive,
            event.get('body', b''),
            event.get('more_body', False)
        )
        try:
            response = await self.handler(
                HttpRequest(
                    self.scope,
                    self.info,
                    {},
                    self.matches,
                    body
                )
            )
        except asyncio.CancelledError:
            return
        except HttpError as error:
            response = HttpResponse(error.status, error.headers, error.body)

        # Finally handle sending the body and the disconnect.
        try:
            # Typically the request handler has already processed the request
            # body, but we flush all the "http.request" messages so we can catch
            # the final "http.disconnect".
            await body.flush()

            send_task = asyncio.create_task(
                self._send_response(send, response)
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
                    LOGGER.debug('event: %s', event)

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

                    LOGGER.debug('disconnecting')

                    is_connected = False
                elif send_task in done:
                    # Fetch result to trigger possible exceptions
                    send_task.result()

            LOGGER.debug('finish handling request')

        except asyncio.CancelledError:
            pass

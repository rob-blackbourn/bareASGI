"""
HTTP Instance
"""

import asyncio
from asyncio import Queue
import logging
from typing import (
    Any,
    Dict,
    Optional,
    Sequence,
    Set
)

from .middleware import make_middleware_chain
from .types import (
    HttpInternalError,
    HttpDisconnectError,
    HttpError,
    HttpRequest,
    Scope,
    Info,
    Send,
    Receive,
    HttpRouter,
    Context,
    HttpMiddlewareCallback,
    HttpResponse
)
from .utils import anext

LOGGER = logging.getLogger(__name__)


class BodyIterator:
    """Iterate over the body content"""

    def __init__(
            self,
            receive: Receive,
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
        request = await self._receive()
        request_type = request['type']
        LOGGER.debug('Received "%s"', request_type, extra={'request': request})

        if request_type == 'http.disconnect':
            raise HttpDisconnectError

        if request_type != 'http.request':
            LOGGER.error(
                'Failed to understand request type "%s"',
                request_type,
                extra={'request': request}
            )
            raise HttpInternalError

        body = request.get('body', b'')
        self._more_body = request.get('more_body', False)
        return body

    async def flush(self) -> None:
        """Flush all remaining http.request messages"""
        while self._more_body:
            await self._queue.put(await self._read())


Middlewares = Sequence[HttpMiddlewareCallback]


class HttpInstance:
    """An HTTP instance services an HTTP request."""

    def __init__(self, scope: Scope, context: Context, info: Info) -> None:
        """Initialise an HTTP instance

        Args:
            scope (Scope): The ASGI connection scope
            context (Context): The application context
            info (Info): The user provided dictionary
        """
        self.scope = scope
        self.info = info

        # Find the route.
        http_router: HttpRouter = context['router']
        handler, matches = http_router.resolve(scope['method'], scope['path'])
        if handler is None:
            raise ValueError(
                f"Handler not found for {scope['method']} {scope['path']}"
            )
        self.handler, self.matches = handler, matches

        # Apply middleware.
        middleware: Optional[Middlewares] = context['middlewares']
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
        return self._is_http_2 and 'http.response.push' in extensions

    # pylint: disable=too-many-arguments
    async def _send_response(
            self,
            send: Send,
            response: HttpResponse
    ) -> None:
        # Create and send the start response.
        response_start = {
            'type': 'http.response.start',
            'status': response.status
        }
        if response.headers:
            response_start['headers'] = response.headers
        else:
            # Needed for Hypercorn 0.7.1
            response_start['headers'] = []

        LOGGER.debug(
            'Sending "http.response.start" with status %s',
            response.status,
            extra=response_start
        )
        await send(response_start)

        if response.pushes is not None and self._is_http_push_supported:
            for push_path, push_headers in response.pushes:
                LOGGER.debug(
                    'sending "http.response.push" for path "%s"',
                    push_path
                )
                await send({
                    'type': 'http.response.push',
                    'path': push_path,
                    'headers': push_headers
                })

        # Create and send the response body.
        response_body: Dict[str, Any] = {'type': 'http.response.body'}

        # If we don't get a body, just send the basic response.
        try:
            buf = await anext(response.body) if response.body else None
        except StopAsyncIteration:
            buf = None
        if buf is None:
            LOGGER.debug(
                'Sending "http.response.body" with empty body',
                extra=response_body
            )
            await send(response_body)
            return

        # Continue to get and send the body until exhausted.
        while buf is not None:
            response_body['body'] = buf
            try:
                buf = await anext(response.body)
                response_body['more_body'] = True
            except StopAsyncIteration:
                buf = None
                response_body['more_body'] = False
            LOGGER.debug(
                'Sending "http.response.body" with more_body="%s',
                response_body["more_body"],
                extra=response_body
            )
            if response_body['body']:
                await send(response_body)

    async def __call__(self, receive: Receive, send: Send) -> None:

        LOGGER.debug('start handling request')

        # The first step is to receive the ASGI request.
        try:
            request = await receive()
            if request['type'] != 'http.request':
                raise HttpInternalError('Expected http.request')
        except asyncio.CancelledError:
            # At this stage we only handle a cancellation. All
            # other errors fall through to the ASGI server.
            return

        # The next step is to call the handler.
        body = BodyIterator(
            receive,
            request.get('body', b''),
            request.get('more_body', False)
        )
        try:
            response = await self.handler(
                HttpRequest(
                    self.scope,
                    self.info,
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
                    request = receive_task.result()
                    LOGGER.debug('request: %s', request)

                    # Cancel pending tasks.
                    for task in pending:
                        try:
                            task.cancel()
                            await task
                        except:  # pylint: disable=bare-except
                            pass

                    # Check for abnormal disconnection.
                    if request['type'] != 'http.disconnect':
                        raise HttpInternalError(
                            'Unexpected request type "{request["type"]}"'
                        )

                    LOGGER.debug('disconnecting')

                    is_connected = False
                elif send_task in done:
                    # Fetch result to trigger possible exceptions
                    send_task.result()

            LOGGER.debug('finish handling request')

        except asyncio.CancelledError:
            pass

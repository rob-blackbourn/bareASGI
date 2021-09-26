# Routing

The routers are split into two: HTTP and WebSockets. A basic router is provided, but this can be replaced if
required.

## HttpRouter

The HTTP router has the following structure:

```python
class HttpRouter:

    @property
    def not_found_response(self):
        ...

    @not_found_response.setter
    def not_found_response(self, value: HttpResponse):
        ...

    def add(self, methods: AbstractSet[str], path: str, callback: HttpRequestCallback) -> None:
        ...

    def __call__(self, scope: Scope) -> Tuple[Optional[HttpRequestCallback], Optional[Mapping[str, Any]]]:
        ...
```

## WebSocketRouter

The WebSocket router has the following structure:

```python
class WebSocketRouter(metaclass=ABCMeta):

    def add(self, path: str, callback: WebSocketRequestCallback) -> None:
        ...

    def __call__(self, scope: Scope) -> Tuple[Optional[WebSocketRequestCallback], Optional[Mapping[str, Any]]]:
        ...
```

## Paths

Here are some example paths:

```python
literal_path = '/foo/bar'
capture_trailing_paths = '/foo/{path}'
variables_path = '/foo/{name}/{id:int}/{created:datetime:%Y-%m-%d}'
```

Matched path segments are passed in to the handlers as a dictionary of route matches.

# Application

The application class has the following constructor:

```python
Application(
    middlewares: Optional[List[HttpMiddlewareCallback]],
    http_router: Optional[HttpRouter],
    web_socket_router: Optional[WebSocketRouter],
    startup_handlers: Optional[List[StartupHandler]],
    shutdown_handlers: Optional[List[ShutdownHandler]],
    not_found_response: Optional[HttpResponse],
    info: Optional[MutableMapping[str, Any]]
)
```

All arguments are optional.

The `info` argument provides a place for application specific data.

The application provides some properties that can be used for configuration:

```python
Application.info -> MutableMapping[str, Any]
Application.middlewares -> List[]
Application.http_router -> HttpRouter
Application.ws_router-> WebSocketRouter
Application.startup_handlers -> List[StartupHandler]
Application.shutdown_handlers -> List[ShutdownHandler]
```

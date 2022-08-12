import functools
from inspect import Parameter, signature
import logging
import traceback
from typing import Any, Callable
from nanohttpy.exceptions import HttpError
from nanohttpy.requests import Request
from nanohttpy.responses import Response, adapt_response
from nanohttpy.routing import Router
from nanohttpy.logging import logger
from nanohttpy.types import DecoratedHandlerFunc, HandlerFunc


class NanoHttpy:
    _debug: bool
    _router: Router

    def __init__(self, debug=False) -> None:
        if debug:
            logger.warning('Running in "debug" mode. Remove debug=True in production.')
            # TODO: actually, even in debug the user should see the debug logs of the framework
            logger.setLevel(logging.DEBUG)

        self._router = Router()

    def _generate_handler_decorator(
        self, http_method: str, path: str
    ) -> Callable[[HandlerFunc], DecoratedHandlerFunc]:
        def handler(func: HandlerFunc) -> DecoratedHandlerFunc:
            @functools.wraps(func)
            def handler_wrapper(req: Request) -> HandlerFunc:
                args: list[Any] = []
                sig = signature(func)
                expected_params = [p for p in sig.parameters.values() if p.kind == Parameter.POSITIONAL_OR_KEYWORD]
                if len(expected_params) > 0:
                    # The first arg is always the request
                    args.append(req)
                    # For the rest, we test first the path_param, then the query args
                    for arg in expected_params[1:]:
                        v = req.param(arg.name)
                        if v is None:
                            v = req.query(arg.name)
                        args.append(v)
                logger.debug("Calling handler with args %s", args)
                return func(*args)

            self._router.add_route(http_method, path, handler_wrapper)
            return handler_wrapper

        return handler

    def get(self, path: str) -> Callable[[HandlerFunc], DecoratedHandlerFunc]:
        return self._generate_handler_decorator("GET", path)

    def head(self, path: str) -> Callable[[HandlerFunc], DecoratedHandlerFunc]:
        return self._generate_handler_decorator("HEAD", path)

    def post(self, path: str) -> Callable[[HandlerFunc], DecoratedHandlerFunc]:
        return self._generate_handler_decorator("POST", path)

    def put(self, path: str) -> Callable[[HandlerFunc], DecoratedHandlerFunc]:
        return self._generate_handler_decorator("PUT", path)

    def delete(self, path: str) -> Callable[[HandlerFunc], DecoratedHandlerFunc]:
        return self._generate_handler_decorator("DELETE", path)

    def connect(self, path: str) -> Callable[[HandlerFunc], DecoratedHandlerFunc]:
        return self._generate_handler_decorator("CONNECT", path)

    def options(self, path: str) -> Callable[[HandlerFunc], DecoratedHandlerFunc]:
        return self._generate_handler_decorator("OPTIONS", path)

    def trace(self, path: str) -> Callable[[HandlerFunc], DecoratedHandlerFunc]:
        return self._generate_handler_decorator("TRACE", path)

    def lookup(self, req: Request) -> HandlerFunc:
        handler = self._router.get_handler(req)
        return handler

    def handle(self, req: Request) -> Response:
        try:
            handler = self.lookup(req)
            return adapt_response(handler(req))
        except HttpError as e:
            # TODO: special Response subtype for errors ?
            # TODO: What about description ?
            return Response(status_code=e.code)
        except BaseException as e:  # pylint: disable=broad-except
            logger.error("%s\n%s", e, traceback.format_exc())
            return Response(status_code=500)

    def run(self, port=5000):
        # We import inside the method to limit the import overhead when the user uses a custom engine
        # And btw it gets rid of the cyclic dep between the PythonEngine and this class
        from nanohttpy.engines.python import (  # pylint: disable=import-outside-toplevel
            PythonEngine,
        )

        engine_class = PythonEngine

        logger.info(
            "Creating an Engine instance of type <%s.%s>",
            engine_class.__module__,
            engine_class.__name__,
        )
        engine = engine_class(("", port), self)

        logger.info("Running on http://127.0.0.1:%d (Press CTRL+C to quit)", port)
        engine.serve_forever()

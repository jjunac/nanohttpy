import functools
import logging
from typing import Any, Callable, Tuple
from nanohttpy.exceptions import HttpError
from nanohttpy.responses import Response, adapt_response
from nanohttpy.routing import Params, Router, HandlerFunc
from nanohttpy.logging import logger


class Nanohttpy:
    _debug: bool
    _router: Router

    def __init__(self, debug=False) -> None:
        if debug:
            logger.warning('Running in "debug" mode. Remove debug=True in production.')
            logger.setLevel(logging.DEBUG)

        self._router = Router()

    def get(self, path: str) -> Callable[[HandlerFunc], HandlerFunc]:
        def handler(func: HandlerFunc) -> HandlerFunc:
            @functools.wraps(func)
            def handler_wrapper(*args, **kwargs) -> HandlerFunc:
                return func(*args, **kwargs)

            self._router.add_route("GET", path, handler_wrapper)
            return handler_wrapper

        return handler

    def lookup(self, method: str, path: str) -> Tuple[HandlerFunc, Params]:
        params: Params = {}
        handler = self._router.get_handler(method, path, params)
        return handler, params

    def handle(self, method: str, path: str) -> Response:
        try:
            handler, params = self.lookup(method, path)
            return adapt_response(handler(**params))
        except HttpError as e:
            # TODO: special Response subtype for errors ?
            # TODO: What about description ?
            return Response(status_code=e.code)
        except BaseException:  # pylint: disable=broad-except
            return Response(status_code=500)

    def run(self, port=5000):
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

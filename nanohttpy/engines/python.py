from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import cast
from ..applications import Nanohttpy


HTTP_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE"]


class _PythonEngineHandler(BaseHTTPRequestHandler):
    def _get_app(self) -> Nanohttpy:
        return cast(PythonEngine, self.server).app

    def generic_do(self, method: str, path: str) -> None:
        response = self._get_app().handle(method, path)
        self.send_response(response.status_code)
        for k, v in response.headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(response.encoded_body)


def _init():
    """Method called on module first import"""

    def generate_http_callback(http_method: str):
        def http_callback(self: _PythonEngineHandler) -> None:
            self.generic_do(http_method, self.path)

        return http_callback

    # Generate the do_(GET|POST|DELETE|...) methods to _PythonEngineHandler
    for http_method in HTTP_METHODS:
        setattr(
            _PythonEngineHandler,
            "do_" + http_method,
            generate_http_callback(http_method),
        )


_init()


class PythonEngine(HTTPServer):
    app: Nanohttpy

    def __init__(self, server_address: tuple[str, int], app: Nanohttpy) -> None:
        HTTPServer.__init__(self, server_address, _PythonEngineHandler)
        self.app = app

    def serve_forever(self, poll_interval: float = 0.5):
        HTTPServer.serve_forever(self, poll_interval)

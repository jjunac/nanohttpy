from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import cast

from nanohttpy.http import HTTP_METHODS, HTTPHeaders
from nanohttpy.applications import NanoHttpy
from nanohttpy.requests import Request


class _PythonEngineHandler(BaseHTTPRequestHandler):
    def _get_app(self) -> NanoHttpy:
        return cast(PythonEngine, self.server).app

    def generic_do(self, method: str, read_body=True) -> None:
        request = Request(
            method,
            self.path,
            self.request_version,
            cast(HTTPHeaders, self.headers),
            # TODO: handle Transfer-Encoding etc...
            self.rfile.read(int(self.headers["Content-Length"])) if read_body else b'',
        )
        response = self._get_app().handle(request)
        self.send_response(response.status_code)
        for k, v in response.headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(response.encoded_body)


def _init():
    """Method called once on module import"""

    def generate_http_callback(http_method: str):
        read_body = http_method not in ("GET", "DELETE")
        def http_callback(self: _PythonEngineHandler) -> None:
            self.generic_do(http_method, read_body=read_body)

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
    app: NanoHttpy

    def __init__(self, server_address: tuple[str, int], app: NanoHttpy) -> None:
        HTTPServer.__init__(self, server_address, _PythonEngineHandler)
        self.app = app

    def serve_forever(self, poll_interval: float = 0.5):
        HTTPServer.serve_forever(self, poll_interval)

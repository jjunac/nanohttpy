import uvloop
import asyncio
from  httptools.parser.parser import HttpRequestParser
from typing import Any, Tuple
from aiohttp.http import StreamWriter
from aiohttp.base_protocol import BaseProtocol
from multidict import CIMultiDict

from nanohttpy.applications import NanoHttpy
from nanohttpy.requests import Request
from nanohttpy.http import HTTPHeaders

class _HttpProtocol(BaseProtocol):
    _app: NanoHttpy
    _current_parser: Any
    _current_url: str
    _current_headers: HTTPHeaders
    _current_body: bytes

    def __init__(self, app: NanoHttpy, loop: asyncio.BaseEventLoop):
        super().__init__(loop)
        self._app = app
        self.reset()

    def reset(self):
        self._current_parser = None
        self._current_url = ''
        self._current_headers = {}
        self._current_body = b''

    def connection_made(self, transport: asyncio.BaseTransport):
        super().connection_made(transport)
        self.reset()
        self._current_parser = HttpRequestParser(self)

    def connection_lost(self, exc):
        super().connection_lost(exc)
        self._current_parser = None

    def data_received(self, data):
        self._current_parser.feed_data(data)

    def on_message_begin(self):
        pass

    def on_url(self, url: bytes):
        self._current_url = url.decode()

    def on_header(self, name: bytes, value: bytes):
        self._current_headers[name.decode()] = value.decode()

    def on_headers_complete(self):
        pass

    def on_body(self, body: bytes):
        self._current_body = body

    def on_message_complete(self):
        self._current_request = Request(
            self._current_parser.get_method().decode(),
            self._current_url,
            self._current_parser.get_http_version(),
            self._current_headers,
            self._current_body,
        )
        asyncio.ensure_future(self.handle(self._current_request), loop=self._loop)

    async def handle(self, request):
        response = self._app.handle(request)

        writer = StreamWriter(self, self._loop)

        status_line = f"HTTP/{request.request_version} {response.status_code} {response.status_reason}"
        await writer.write_headers(status_line, CIMultiDict(response.headers))
        await writer.write(response.encoded_body)
        await writer.write_eof()

        self.transport.close()



class UvloopEngine:
    app: NanoHttpy
    server: asyncio.Server
    loop: asyncio.BaseEventLoop

    def __init__(self, server_address: Tuple[str, int], app: NanoHttpy) -> None:
        self.app = app

        self.loop = uvloop.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.set_debug(False)

        self.server = self.loop.run_until_complete(
            self.loop.create_server(
                lambda: _HttpProtocol(self.app, self.loop),
                host=server_address[0],
                port=server_address[1],
            )
        )

    def serve_forever(self):
        try:
            self.loop.run_forever()
        finally:
            self.server.close()
            self.loop.close()

import uvloop
import asyncio
import httptools
from typing import Any, Dict, Tuple, overload
from aiohttp import web
from socket import IPPROTO_TCP, TCP_NODELAY

from nanohttpy.applications import NanoHttpy
from nanohttpy.requests import Request


class _HttpProtocol(asyncio.Protocol):

    _loop: asyncio.BaseEventLoop
    _transport: asyncio.BaseTransport
    _current_parser: Any
    _current_url: bytes
    _current_headers: Dict[bytes, bytes]

    def __init__(self, loop):
        print(loop)
        self._loop = loop
        # if loop is None:
        #     loop = asyncio.get_event_loop()
        # self._loop = loop
        # self._transport = None
        # self._current_request = None
        # self._current_parser = None
        # self._current_url = None
        # self._current_headers = None

    @overload
    def connection_made(self, transport: asyncio.BaseTransport):
        self._transport = transport
        self._current_parser = httptools.HttpRequestParser(self)

        sock = transport.get_extra_info("socket")
        try:
            sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        except (OSError, NameError):
            pass

    @overload
    def connection_lost(self, exc):
        self._current_parser = None

    @overload
    def data_received(self, data):
        self._current_parser.feed_data(data)

    def on_message_begin(self):
        pass

    def on_url(self, url: bytes):
        self._current_url = url

    def on_header(self, name, value):
        self._current_headers.append((name, value))

    def on_headers_complete(self):
        self._current_request = HttpRequest(
            self,
            self._current_url,
            self._current_headers,
            self._current_parser.get_http_version(),
        )

        self._loop.call_soon(
            self.handle,
            self._current_request,
            HttpResponse(self, self._current_request),
        )



    # def handle(self, request, response):
    #     parsed_url = httptools.parse_url(self._current_url)
    #     payload_size = parsed_url.path.decode("ascii")[1:]
    #     if not payload_size:
    #         payload_size = 1024
    #     else:
    #         payload_size = int(payload_size)
    #     resp = _RESP_CACHE.get(payload_size)
    #     if resp is None:
    #         resp = b"X" * payload_size
    #         _RESP_CACHE[payload_size] = resp
    #     response.write(resp)
    #     if not self._current_parser.should_keep_alive():
    #         self._transport.close()
    #     self._current_parser = None
    #     self._current_request = None


class UvloopEngine:
    app: NanoHttpy
    server: asyncio.Server
    loop: asyncio.BaseEventLoop

    def __init__(self, server_address: Tuple[str, int], app: NanoHttpy) -> None:
        self.app = app

        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(False)

        self.server = loop.run_until_complete(
            loop.create_server(
                lambda: _HttpProtocol(loop=loop),
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

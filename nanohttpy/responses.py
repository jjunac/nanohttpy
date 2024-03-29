from http import HTTPStatus
import json
from typing import Any, Dict, Optional, Type
from nanohttpy.exceptions import NanoHttpyError

from nanohttpy.logging import logger
from nanohttpy.types import Decorator


_HTTP_HEADER_ENCODING = "iso-8859-1"
_RESPONSE_TYPES: Dict[type, Type["Response"]] = {}


def response_adapter(*adapted_types: type) -> Decorator[Type["Response"]]:
    """Register a Response class as adapter of a type"""

    def decorator_response(cls: Type["Response"]) -> Type["Response"]:
        for t in adapted_types:
            if issubclass(t, tuple):
                raise NanoHttpyError(
                    "Cannot adapt a tuple, as it is used for status_code binding etc..."
                )
            _RESPONSE_TYPES[t] = cls
        return cls

    return decorator_response


def adapt_response(handler_result: Any) -> "Response":
    """Try to detect the suitable type of response depending on type of content and wraps it"""
    if isinstance(handler_result, Response):
        logger.debug(
            "Handler result is an instance of Response %s, returning as-is",
            type(handler_result),
        )
        return handler_result

    content = handler_result
    # Check if the handler tried to return multiple values
    if isinstance(content, tuple):
        content = content[0]

    res = _RESPONSE_TYPES.get(type(content), None)
    if res is None:
        res = Response
        logger.debug(
            "No Response found adapting %s, defaulting to Response", type(content)
        )
    else:
        logger.debug(
            "Content is %s, adapting with <%s.%s>",
            type(content),
            res.__module__,
            res.__name__,
        )

    if isinstance(handler_result, tuple):
        return res(*handler_result)
    else:
        return res(content)


class Response:
    status_code: int
    headers: Dict[str, str]
    encoded_body: bytes
    _media_type: Optional[str] = None
    _charset: str = "utf-8"

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.status_code = status_code
        self.encoded_body = self.render(content)
        self._init_headers(headers)

    def _init_headers(self, headers: Optional[Dict[str, str]]) -> None:
        headers = headers or {}

        headers["Content-Length"] = str(len(self.encoded_body))

        if self.encoded_body and self._media_type is not None:
            content_type = self._media_type
            if self._charset:
                content_type += "; charset=" + self._charset.upper()
            headers["Content-Type"] = content_type

        # Per section 3.3.2 of RFC 7230, "a server MUST NOT send a Content-Length header field in any response with a
        # status code of 1xx (Informational) or 204 (No Content)."
        if 100 <= self.status_code < 200 or self.status_code == 204:
            del headers["Content-Length"]
            del headers["Content-Type"]

        self.headers = headers

    @property
    def encoded_headers(self) -> Dict[bytes, bytes]:
        if not hasattr(self, "_encoded_headers"):
            self._encoded_headers: Dict[  # pylint: disable=attribute-defined-outside-init
                bytes, bytes
            ] = {
                k.encode(_HTTP_HEADER_ENCODING): v.encode(_HTTP_HEADER_ENCODING)
                for k, v in self.headers.items()
            }
        return self._encoded_headers

    @property
    def status_reason(self) -> str:
        return HTTPStatus(self.status_code).phrase

    def render(self, content: Any) -> bytes:
        if content is None:
            return b""
        if isinstance(content, bytes):
            return content
        return content.encode(self._charset)


@response_adapter(bytes, str)
class PlainTextResponse(Response):
    _media_type = "text/plain"


@response_adapter(dict)
class JSONResponse(Response):
    _media_type = "application/json"

    def render(self, content: Any) -> bytes:
        # Since we encoded in utf-8, no need to worry about ensure_ascii
        return json.dumps(
            content, ensure_ascii=False, allow_nan=False, separators=(",", ":")
        ).encode(
            self._charset,
        )

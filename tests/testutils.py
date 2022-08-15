from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar, Union
import pytest
from nanohttpy.http import HTTPHeaders
from nanohttpy.requests import Request

E = TypeVar("E", bound=BaseException)


def assert_raises(
    exception: Union[Type[E], Tuple[Type[E], ...]],
    f: Callable[[], Any],
    match: Optional[str] = None,
):
    with pytest.raises(exception, match=match):
        f()


def make_request(
    method: str,
    full_path: str,
    request_version: str = "HTTP/1.1",
    headers: HTTPHeaders = HTTPHeaders(),
    body: bytes = b"",
    path_parameters: Dict[str, str] = None
) -> Request:
    req = Request(method, full_path, request_version, headers, body)
    req.path_parameters = path_parameters or {} 
    return req

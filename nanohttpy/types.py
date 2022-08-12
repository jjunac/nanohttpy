from typing import Callable, Any, TypeVar

from nanohttpy.requests import Request

T = TypeVar("T")

Decorator = Callable[[T], T]
HandlerFunc = Callable[..., Any]
DecoratedHandlerFunc = Callable[[Request], Any]


from typing import Callable, Any, TypeVar

T = TypeVar('T')

Decorator = Callable[[T], T]
HandlerFunc = Callable[..., Any]


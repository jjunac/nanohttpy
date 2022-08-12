from typing import Any, Callable, Optional, Type, TypeVar, Union
import pytest

E = TypeVar("E", bound=BaseException)


def assert_raises(
    exception: Union[Type[E], tuple[Type[E], ...]],
    f: Callable[[], Any],
    match: Optional[str] = None,
):
    with pytest.raises(exception, match=match):
        f()

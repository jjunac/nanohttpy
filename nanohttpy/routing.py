from operator import xor
from os import pathconf
import re
from typing import Callable, Any, Generator, Optional

from nanohttpy.exceptions import MethodNotAllowedError, NanohttpyError, NotFoundError
from nanohttpy.logging import logger


HandlerFunc = Callable[..., Any]
Params = dict[str, Any]


class RouteTree:
    path: str
    _method_handlers: dict[str, HandlerFunc]
    _children: dict[str, "RouteTree"]
    _wild_child: Optional["RouteTree"]

    def __init__(
        self,
        path: str,
        method_handlers: dict[str, HandlerFunc] = None,
        children: dict[str, "RouteTree"] = None,
        wild_child: Optional["RouteTree"] = None,
    ) -> None:
        self.path = path
        self._method_handlers = method_handlers or {}
        self._children = children or {}
        self._wild_child = wild_child

    def get_child(self, path: str, params: Params) -> Optional["RouteTree"]:
        res = self._children.get(path, None)
        # If we didn't find a specialized URL, we check if there is a wildcard
        if res is None and self._wild_child is not None:
            # Assign the path param value
            params[self._wild_child.path[1:-1]] = path
            res = self._wild_child
        return res

    def get_or_create_child(self, path: str) -> "RouteTree":
        return self._children.setdefault(path, RouteTree(path))

    def get_wild_child(self) -> Optional["RouteTree"]:
        return self._wild_child

    def get_or_create_wild_child(self, path) -> "RouteTree":
        if self._wild_child is None:
            self._wild_child = RouteTree(path)
        return self._wild_child

    def has_handler(self, method: str) -> bool:
        return self._method_handlers.get(method, None) is not None

    def get_handler(self, method: str) -> Optional[HandlerFunc]:
        return self._method_handlers.get(method, None)

    def set_handler(self, method: str, handler: HandlerFunc) -> None:
        self._method_handlers[method] = handler


def tokenize_path(path: str) -> Generator[str, None, None]:
    """
    Tokenize a path with / as delimiter, omitting empty tokens
    """
    for path_comp in path.split("/"):
        if path_comp == "":
            continue
        yield path_comp


def check_param(path_comp) -> bool:
    """
    Check if a path component is a parameter. Throws if path_comp contains { or } in the middle or the string, or only opening/closing
    """
    if m := re.search(r"[{}]", path_comp[1:-1]):
        raise NanohttpyError(f"Unexpected {m.group(0)}")
    if xor(path_comp[0] == "{", path_comp[-1] == "}"):
        raise NanohttpyError("Unbalanced { } found")
    return path_comp[0] == "{"


class Router:
    _route_tree: RouteTree

    def __init__(self) -> None:
        self._route_tree = RouteTree("")

    def add_route(self, method: str, path: str, handler: HandlerFunc):
        # TODO: pre-validation to avoid error handling in the middle + better error message ?
        curr_route = self._route_tree
        for path_comp in tokenize_path(path):
            if check_param(path_comp):
                curr_route = curr_route.get_or_create_wild_child(path_comp)
                if curr_route.path != path_comp:
                    raise NanohttpyError(
                        f"Found handler with different wildcard '{curr_route.path}' name for request '{method} {path}'"
                    )
            else:
                curr_route = curr_route.get_or_create_child(path_comp)
        if curr_route.has_handler(method):
            raise NanohttpyError(
                f"A handler is already registered for request '{method} {path}'"
            )
        curr_route.set_handler(method, handler)
        logger.debug(
            "Handler <%s> set for request '%s %s'", handler.__name__, method, path
        )

    def get_handler(self, method: str, path: str, params: Params) -> HandlerFunc:
        logger.debug("Matching route for request '%s %s'...", method, path)
        curr_route = self._route_tree
        for path_comp in tokenize_path(path):
            opt_route = curr_route.get_child(path_comp, params)
            if opt_route is None:
                logger.debug("No match found for path component '%s'", path_comp)
                raise NotFoundError()
            curr_route = opt_route

        handler = curr_route.get_handler(method)
        if handler is None:
            logger.debug("Method %s not allowed for path '%s'", method, path)
            raise MethodNotAllowedError()

        logger.debug(
            "Found handler <%s> for request '%s %s'...", handler.__name__, method, path
        )
        return handler

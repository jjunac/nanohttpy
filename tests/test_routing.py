# pylint: disable=multiple-statements,invalid-name,too-many-statements,use-implicit-booleaness-not-comparison
import pytest
from nanohttpy.http import HTTPHeaders
from nanohttpy.requests import Request
from nanohttpy.routing import RouteTree, Router, check_param, tokenize_path
from nanohttpy.exceptions import MethodNotAllowedError, NanoHttpyError, NotFoundError

from tests.testutils import assert_raises, make_request


@pytest.mark.parametrize(
    "input_path, expected",
    [
        ("/this/is/a/path", ["this", "is", "a", "path"]),
        ("/this/is/a/path/", ["this", "is", "a", "path"]),
        ("this/is/a/path/", ["this", "is", "a", "path"]),
        ("//this/is//a/path////", ["this", "is", "a", "path"]),
        ("/a/b", ["a", "b"]),
        ("/a/b/", ["a", "b"]),
        ("a/b/", ["a", "b"]),
        ("/a", ["a"]),
        ("a", ["a"]),
        ("a/", ["a"]),
        ("/a/", ["a"]),
        ("///a///", ["a"]),
    ],
)
def test_tokenize_path(input_path, expected):
    assert list(tokenize_path(input_path)) == expected


def test_check_param():
    #  FastAPI-like path parameters
    assert check_param("{param}")
    assert check_param("<param>")
    assert not check_param("param")

    assert_raises(NanoHttpyError, lambda: check_param("{param"))
    assert_raises(NanoHttpyError, lambda: check_param("param}"))
    assert_raises(NanoHttpyError, lambda: check_param("par{am"))
    assert_raises(NanoHttpyError, lambda: check_param("pa}ram"))
    assert_raises(NanoHttpyError, lambda: check_param("{{param}"))

    assert_raises(NanoHttpyError, lambda: check_param("<param"))
    assert_raises(NanoHttpyError, lambda: check_param("param>"))
    assert_raises(NanoHttpyError, lambda: check_param("par<am"))
    assert_raises(NanoHttpyError, lambda: check_param("pa>ram"))
    assert_raises(NanoHttpyError, lambda: check_param("<<param>"))

    assert_raises(NanoHttpyError, lambda: check_param("{par<am}"))
    assert_raises(NanoHttpyError, lambda: check_param("<par{am>"))
    assert_raises(NanoHttpyError, lambda: check_param("<param}"))


def test_RouteTree():
    rt = RouteTree("parent")

    # Verify default state
    assert rt.get_child("child1", {}) is None
    assert rt.get_child("child2", {}) is None
    assert rt.get_child("key", {}) is None
    assert rt.get_wild_child() is None

    # Verify default state
    assert rt.get_child("child1", {}) is None
    assert rt.get_child("child2", {}) is None
    assert rt.get_child("key", {}) is None
    assert rt.get_wild_child() is None

    rt.get_or_create_child("child1")

    # Now there just is child1 that is not None
    assert rt.get_child("child1", {}) is not None
    assert rt.get_child("child2", {}) is None
    assert rt.get_child("key", {}) is None
    assert rt.get_wild_child() is None

    # Check that if we call twice get_or_create_child we get the same node
    assert rt.get_or_create_child("child1") == rt.get_or_create_child("child1")

    rt.get_or_create_child("child2")

    # child1 and child2 are not None
    assert rt.get_child("child1", {}) is not None
    assert rt.get_child("child2", {}) is not None
    assert rt.get_child("key", {}) is None
    assert rt.get_wild_child() is None

    # Check that nothing is handled for now
    assert not rt.has_handler("GET")
    assert rt.get_handler("GET") is None
    assert not rt.has_handler("POST")
    assert rt.get_handler("POST") is None
    assert not rt.has_handler("DELETE")
    assert rt.get_handler("DELETE") is None

    def parent_get():
        pass

    rt.set_handler("GET", parent_get)

    # Check that the GET is handled is handled
    assert rt.has_handler("GET")
    assert rt.get_handler("GET").__name__ == "parent_get"
    assert not rt.has_handler("POST")
    assert rt.get_handler("POST") is None
    assert not rt.has_handler("DELETE")
    assert rt.get_handler("DELETE") is None

    def parent_post():
        pass

    rt.set_handler("POST", parent_post)

    # Check that the GET is handled is handled
    assert rt.has_handler("GET")
    assert rt.get_handler("GET").__name__ == "parent_get"
    assert rt.has_handler("POST")
    assert rt.get_handler("POST").__name__ == "parent_post"
    assert not rt.has_handler("DELETE")
    assert rt.get_handler("DELETE") is None

    # Check the children initial state
    assert rt.get_child("child1", {}).get_handler("GET") is None
    assert rt.get_child("child2", {}).get_handler("GET") is None

    # Set the handler for the children
    def child1_get():
        pass

    def child2_get():
        pass

    rt.get_child("child1", {}).set_handler("GET", child1_get)
    rt.get_child("child2", {}).set_handler("GET", child2_get)

    assert rt.get_child("child1", {}).get_handler("GET").__name__ == "child1_get"
    assert rt.get_child("child2", {}).get_handler("GET").__name__ == "child2_get"

    # Check the wild child initial state
    assert rt.get_wild_child() is None
    assert rt.get_child("key", {}) is None
    assert rt.get_child("whatever", {}) is None

    rt.get_or_create_wild_child("path_param")

    assert rt.get_or_create_wild_child("path_param") == rt.get_or_create_wild_child(
        "path_param"
    )
    assert rt.get_or_create_wild_child("path_param").get_handler("GET") is None

    def wild_get():
        pass

    rt.get_wild_child().set_handler("GET", wild_get)
    assert (
        rt.get_or_create_wild_child("path_param").get_handler("GET").__name__
        == "wild_get"
    )

    # Check that the old route still stand and the wild child take over if no other child is matching
    assert rt.get_handler("GET").__name__ == "parent_get"
    params = {}
    assert rt.get_child("child1", params).get_handler("GET").__name__ == "child1_get"
    assert params == {}
    assert rt.get_child("child2", params).get_handler("GET").__name__ == "child2_get"
    assert params == {}
    assert rt.get_child("key", params).get_handler("GET").__name__ == "wild_get"
    assert params == {"path_param": "key"}
    assert rt.get_child("whatever", params).get_handler("GET").__name__ == "wild_get"
    assert params == {"path_param": "whatever"}


def test_Router():
    r = Router()

    def root():
        pass

    def param1():
        pass

    def a():
        pass

    def a_b():
        pass

    def a_b_param3():
        pass

    def param1_b():
        pass

    def param1_param2():
        pass

    assert_raises(
        MethodNotAllowedError, lambda: r.get_handler(make_request("GET", "/"))
    )
    assert_raises(NotFoundError, lambda: r.get_handler(make_request("GET", "/a")))
    assert_raises(
        NotFoundError, lambda: r.get_handler(make_request("GET", "/whatever"))
    )

    r.add_route("GET", "/", root)

    assert r.get_handler(make_request("GET", "/")) is not None
    assert_raises(NotFoundError, lambda: r.get_handler(make_request("GET", "/a")))
    assert_raises(
        NotFoundError, lambda: r.get_handler(make_request("GET", "/whatever"))
    )

    r.add_route("GET", "/a", a)

    assert r.get_handler(make_request("GET", "/a")) is not None
    assert_raises(
        NotFoundError, lambda: r.get_handler(make_request("GET", "/whatever"))
    )

    r.add_route("GET", "/{param1}", param1)

    assert r.get_handler(make_request("GET", "/")) is not None
    assert r.get_handler(make_request("GET", "/a")) is not None
    assert r.get_handler(make_request("GET", "/whatever")) is not None

    r.add_route("GET", "/a/b", a_b)
    r.add_route("GET", "/a/b/{param3}", a_b_param3)
    r.add_route("GET", "/{param1}/b", param1_b)
    r.add_route("GET", "/{param1}/{param2}", param1_param2)

    # Handler already registered
    assert_raises(NanoHttpyError, lambda: r.add_route("GET", "/", root))

    # Handler already registered with different path_param
    assert_raises(NanoHttpyError, lambda: r.add_route("GET", "/{different}", param1))

    req = make_request("GET", "/")
    assert r.get_handler(req).__name__ == "root"
    assert req.path_parameters == {}
    req = make_request("GET", "")
    assert r.get_handler(req).__name__ == "root"
    assert req.path_parameters == {}
    req = make_request("GET", "///")
    assert r.get_handler(req).__name__ == "root"
    assert req.path_parameters == {}

    req = make_request("GET", "/a")
    assert r.get_handler(req).__name__ == "a"
    assert req.path_parameters == {}
    req = make_request("GET", "a")
    assert r.get_handler(req).__name__ == "a"
    assert req.path_parameters == {}
    req = make_request("GET", "/a/")
    assert r.get_handler(req).__name__ == "a"
    assert req.path_parameters == {}

    req = make_request("GET", "/something")
    assert r.get_handler(req).__name__ == "param1"
    assert req.path_parameters == {"param1": "something"}

    req = make_request("GET", "/whatever")
    assert r.get_handler(req).__name__ == "param1"
    assert req.path_parameters == {"param1": "whatever"}

    req = make_request("GET", "/a/b")
    assert r.get_handler(req).__name__ == "a_b"
    assert req.path_parameters == {}

    req = make_request("GET", "/a/b/whatev")
    assert r.get_handler(req).__name__ == "a_b_param3"
    assert req.path_parameters == {"param3": "whatev"}

    req = make_request("GET", "/key/b")
    assert r.get_handler(req).__name__ == "param1_b"
    assert req.path_parameters == {"param1": "key"}

    req = make_request("GET", "/key/another-key")
    assert r.get_handler(req).__name__ == "param1_param2"
    assert req.path_parameters == {"param1": "key", "param2": "another-key"}

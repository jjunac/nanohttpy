# pylint: disable=invalid-name, multiple-statements, too-many-statements, use-implicit-booleaness-not-comparison, unused-argument
import inspect
import pytest

from nanohttpy.applications import NanoHttpy
from tests.testutils import make_request


@pytest.mark.parametrize(
    "url, func_name, params",
    [
        ("/no_param", "no_param", {}),
        ("/only_req", "only_req", {"req": make_request("GET", "/only_req")}),
        (
            "/req_1_path_param/value1",
            "req_1_path_param",
            {
                "req": make_request(
                    "GET",
                    "/req_1_path_param/value1",
                    path_parameters={"param1": "value1"},
                ),
                "param1": "value1",
            },
        ),
        (
            "/req_2_path_param/value1/value2",
            "req_2_path_param",
            {
                "req": make_request(
                    "GET",
                    "/req_2_path_param/value1/value2",
                    path_parameters={"param1": "value1", "param2": "value2"},
                ),
                "param1": "value1",
                "param2": "value2",
            },
        ),
        (
            "/req_ignore_path_param/value1",
            "req_ignore_path_param",
            {
                "req": make_request(
                    "GET",
                    "/req_ignore_path_param/value1",
                    path_parameters={"param1": "value1"},
                ),
            },
        ),
        (
            "/req_qs?client=firefox&q=test",
            "req_qs",
            {
                "req": make_request(
                    "GET",
                    "/req_qs?client=firefox&q=test",
                ),
                "client": "firefox",
                "q": "test",
            },
        ),
        (
            "/req_ignored_qs?client=firefox&q=test",
            "req_ignored_qs",
            {
                "req": make_request(
                    "GET",
                    "/req_ignored_qs?client=firefox&q=test",
                ),
            },
        ),
        (
            "/req_path_param_and_qs/value1?client=firefox&q=test",
            "req_path_param_and_qs",
            {
                "req": make_request(
                    "GET",
                    "/req_path_param_and_qs/value1?client=firefox&q=test",
                    path_parameters={"param1": "value1"},
                ),
                "param1": "value1",
                "client": "firefox",
                "q": "test",
            },
        ),
        (
            "/req_conflicting_path_param_and_qs/path-value?param1=qs-value",
            "req_conflicting_path_param_and_qs",
            {
                "req": make_request(
                    "GET",
                    "/req_conflicting_path_param_and_qs/path-value?param1=qs-value",
                    path_parameters={"param1": "path-value"},
                ),
                # The path parameter takes precedence for the query arg
                "param1": "path-value",
            },
        ),
    ],
)
def test_NanoHttpy_handler_decorator(url, func_name, params):
    app = NanoHttpy(debug=True)

    @app.get("/no_param")
    def no_param():
        return inspect.stack()[0][3], locals()

    @app.get("/only_req")
    def only_req(req):
        return inspect.stack()[0][3], locals()

    @app.get("/req_1_path_param/{param1}")
    def req_1_path_param(req, param1):
        return inspect.stack()[0][3], locals()

    @app.get("/req_2_path_param/{param1}/{param2}")
    def req_2_path_param(req, param1, param2):
        return inspect.stack()[0][3], locals()

    @app.get("/req_ignore_path_param/{param1}")
    def req_ignore_path_param(req):
        return inspect.stack()[0][3], locals()

    @app.get("/req_qs")
    def req_qs(req, client, q):
        return inspect.stack()[0][3], locals()

    @app.get("/req_ignored_qs")
    def req_ignored_qs(req):
        return inspect.stack()[0][3], locals()

    @app.get("/req_path_param_and_qs/{param1}")
    def req_path_param_and_qs(req, param1, client, q):
        return inspect.stack()[0][3], locals()

    @app.get("/req_conflicting_path_param_and_qs/{param1}")
    def req_conflicting_path_param_and_qs(req, param1):
        return inspect.stack()[0][3], locals()

    req = make_request("GET", url)
    assert app.lookup(req)(req) == (func_name, params)

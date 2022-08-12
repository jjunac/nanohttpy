# pylint: disable=multiple-statements,invalid-name,too-many-statements,use-implicit-booleaness-not-comparison
import pytest
from nanohttpy.http import URL, HTTPHeaders
from nanohttpy.requests import Request

from tests.testutils import assert_raises, make_request


def relative_URL(path: str, query: str, fragment: str) -> URL:
    return URL("", "", "", path, query, fragment)

@pytest.mark.parametrize(
    "input_url, expected_url, expected_args",
    [
        (
            "/path/only",
            relative_URL("/path/only", "", ""),
            {},
        ),
        (
            "/?query=only",
            relative_URL("/", "query=only", ""),
            {"query": ["only"]},
        ),
        (
            "/#fragment-only",
            relative_URL("/", "", "fragment-only"),
            {},
        ),
        (
            "/search?client=firefox-b-d&q=test#fragment",
            relative_URL("/search", "client=firefox-b-d&q=test", "fragment"),
            {"client": ["firefox-b-d"], "q": ["test"]},
        ),
        (
            "/multiple-qs?var=value1&var=value2",
            relative_URL("/multiple-qs", "var=value1&var=value2", ""),
            {"var": ["value1", "value2"]},
        ),
        (
            "/path/to/resource?path=/path/in/qs#/path/in/fragment",
            relative_URL("/path/to/resource", "path=/path/in/qs", "/path/in/fragment"),
            {"path": ["/path/in/qs"]},
        ),
    ],
)
def test_Request_url_parsing(input_url: str, expected_url: URL, expected_args: dict):
    req = make_request("", input_url)
    assert req.url == expected_url
    assert req.args == expected_args



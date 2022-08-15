from dataclasses import dataclass
from http.client import HTTPMessage
import re
from typing import Dict, List
from urllib.parse import parse_qs


HTTP_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE"]

HTTPHeaders = HTTPMessage

@dataclass
class URL:
    scheme: str
    userinfo: str
    host: str
    path: str
    query: str
    fragment: str


_re_path_query_fragment = re.compile(
    r"(/? [^#?]*) (?: \? ([^#]*) )? (?: \# (.*) )?", re.VERBOSE
)


def fast_parse_request_path(url: str) -> URL:
    """
    Fast URL parsing if we know it's a relative URL, ie. no scheme, host etc...
    URL accepted by the method are in the form '/path/resource?key1=value1&key2=value2#fragment'
    Otherwise undefined behavior.
    ~3x faster than urllib.parse.urlparse
    """
    m = _re_path_query_fragment.match(url)
    path, query, fragment = m.groups("") if m else ("", "", "")
    return URL(
        scheme="",
        userinfo="",
        host="",
        path=path,
        query=query,
        fragment=fragment,
    )


def parse_query_string(query_string: str) -> Dict[str, List[str]]:
    return parse_qs(query_string)

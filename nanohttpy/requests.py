from dataclasses import dataclass, field
from typing import Dict, List, Optional

from nanohttpy.http import URL, HTTPHeaders, fast_parse_request_path, parse_query_string


@dataclass
class Request:  # pylint: disable=too-many-instance-attributes
    method: str
    full_path: str  # Requested path, including query string and fragment
    request_version: str
    headers: HTTPHeaders
    body: bytes
    url: URL = field(init=False)
    args: Dict[str, List[str]] = field(init=False)  # The parsed URL params, compatibility with Flask
    path_parameters: Dict[str, str] = field(init=False)

    def __post_init__(self):
        self.url = fast_parse_request_path(self.full_path)
        self.args = parse_query_string(self.url.query) if self.url.query else {}
        self.path_parameters = {}

    def query(self, key: str, default: str = None) -> Optional[str]:
        """
        Returns the first query value if exists, otherwise default.
        Shortcut for `args[key][0]`.
        """
        res = self.args.get(key, [])
        return res[0] if res else default

    def param(self, key: str, default: str = None) -> Optional[str]:
        """
        Returns the value of a path parameter if exists, otherwise default.
        Shortcut for `path_parameters.get(key, default)`.
        """
        return self.path_parameters.get(key, default)




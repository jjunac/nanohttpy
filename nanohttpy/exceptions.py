import http


class NanoHttpyError(RuntimeError):
    pass


class HttpError(NanoHttpyError):
    code: int
    description: str

    def __str__(self) -> str:
        return f"{self.code} {http.client.responses[self.code]}: {self.description}"


class NotFoundError(HttpError):
    code = 404
    description = "The requested URL was not found on the server"


class MethodNotAllowedError(HttpError):
    code = 405
    description = "The method is not allowed for the requested URL"

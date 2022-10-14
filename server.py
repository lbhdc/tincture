import inspect
import re
from typing import Callable, TypeAlias, Pattern
from urllib.parse import parse_qs
from wsgiref.headers import Headers
from wsgiref.simple_server import make_server


class Request:
    def __init__(self, environ: dict[str, str]) -> None:
        self.environ = environ
        self.urlargs = {}

    @property
    def path(self) -> str:
        return self.environ["PATH_INFO"]

    @property
    def query(self) -> dict[str, list[str]]:
        return parse_qs(self.environ["QUERY_STRING"])


class Response:
    def __init__(self, mime_type: str = "text/html") -> None:
        self.status = "200 OK"
        self.headers = Headers([("Content-Type", f"{mime_type}; charset=utf-8")])

    def send(self, start_response: Callable) -> None:
        start_response(self.status, self.headers.items())


Handlerfn: TypeAlias = Callable[[Request, Response], bytes]


class Server:
    def __init__(self, host: str = "", port: int = 8080) -> None:
        self.host = host
        self.port = port
        self.routes: list[tuple[Pattern, Handlerfn]] = []

    def handle(self, path: str) -> Callable[[Handlerfn], Handlerfn]:
        def inner(fn: Handlerfn):
            self.routes.append((re.compile(path), fn))
            return fn
        return inner

    def serve(self) -> None:
        httpd = make_server(self.host, self.port, self)
        httpd.serve_forever()

    def _notfound(self, req: Request, res: Response) -> bytes:
        res.status = "404 Not Found"
        return b"Not Found"

    def __call__(self, environ: dict[str, str], star_response: Callable) -> list[bytes]:
        req = Request(environ)
        routed_handler = self._notfound
        for path_pattern, handler in self.routes:
            if match := path_pattern.fullmatch(req.path):
                routed_handler = handler
                req.urlargs = match.groupdict()
                break
        res = Response()
        if inspect.isclass(routed_handler):
            routed_handler = routed_handler()
        body = routed_handler(req, res)
        res.send(star_response)
        return [body]

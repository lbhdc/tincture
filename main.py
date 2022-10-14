from server import Server, Request, Response
from template import HtmlTemplate

srv = Server()

tpl = """<html>
<head>
  <title>{page_title}</title>
</head>
<body>{page_body}</body>
</html>"""

@srv.handle("/greet")
def greet(req: Request, res: Response) -> bytes:
    msg = "why hello {there}"
    if "name" in req.query and req.query["name"]:
        msg = msg.format(there=req.query["name"][0])
    else:
        msg = msg.format(there="there")
    return HtmlTemplate().format(
        tpl,
        page_title="tincture greeter",
        page_body=msg).encode("utf-8")


if __name__ == "__main__":
    srv.serve()
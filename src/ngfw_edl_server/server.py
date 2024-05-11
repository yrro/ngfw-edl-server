from typing import Final

from flask import Blueprint, make_response, request
from flask.typing import ResponseReturnValue

from . import dns


server: Final = Blueprint("server", __name__)


@server.route("/server/srv/<target>")
def srv(target: str) -> ResponseReturnValue:
    comments = bool(int(request.args.get("comments", "0")))

    content = ""
    for addr, comment in dns.query(target):
        content += addr
        if comments:
            content += "  # " + comment
        content += "\r\n"

    resp = make_response(content)
    resp.headers["Content-Type"] = "text/plain"
    return resp

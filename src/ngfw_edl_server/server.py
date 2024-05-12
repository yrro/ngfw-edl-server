from quart import Blueprint, make_response, request
from quart.typing import ResponseReturnValue

from . import dns


blueprint = Blueprint("server", __name__)


@blueprint.route("/srv/<target>")
async def srv(target: str) -> ResponseReturnValue:
    comments = bool(int(request.args.get("comments", "0")))

    content = ""
    async for addr, comment in dns.query(target):
        content += addr
        if comments:
            content += "  # " + comment
        content += "\r\n"

    resp = await make_response(content)
    resp.headers["Content-Type"] = "text/plain"
    return resp

from quart import Blueprint, make_response, request
from quart.typing import ResponseReturnValue

from . import dns


blueprint = Blueprint("server", __name__)


@blueprint.route("/srv/<target>")
async def srv(target: str) -> ResponseReturnValue:

    # IP Address Lists formatting guidelines:
    # <https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-admin/policy/use-an-external-dynamic-list-in-policy/formatting-guidelines-for-an-external-dynamic-list/ip-address-list#idd44a975a-a94a-4398-864e-5cf223f1d351>
    #
    # If the target specified is not found in the DNS, we want to return a 500
    # error so that the firewall does not empty out a previously working IP
    # address list. Hence we do not catch the NXDOMAIN error that would be
    # raised by dns.query.
    content = ""
    async for addr, comment in dns.query(target):
        content += addr + "  " + comment
        content += "\r\n"

    resp = await make_response(content)
    resp.headers["Content-Type"] = "text/plain"
    return resp

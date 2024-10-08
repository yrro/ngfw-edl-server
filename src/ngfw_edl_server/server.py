import logging
from typing import cast

from dns.asyncresolver import Resolver
from dns.rrset import RRset
from dns.resolver import NXDOMAIN
from quart import Blueprint, current_app, g, make_response
from quart.typing import ResponseReturnValue

logger = logging.getLogger(__name__)

blueprint = Blueprint("server", __name__)


def get_resolver() -> Resolver:
    if "resolver" not in g:
        g.resolver = Resolver()
        for attr, value in current_app.config["DNSPYTHON_RESOLVER_PROPERTIES"].items():
            setattr(g.resolver, attr, value)

    return cast(Resolver, g.resolver)


@blueprint.route("/srv/<target>")
async def srv(target: str) -> ResponseReturnValue:
    resolver = get_resolver()

    try:
        srv_answer = await resolver.resolve(target, "SRV", lifetime=5, search=False)
    except NXDOMAIN:
        current_app.metric_dns_nxdomain_total.inc({"qname": target, "rdtype": "SRV"})
        logger.warning("NXDOMAIN for %r", target)
        return b"", 400
    logger.debug("Response: %r", srv_answer.response.to_text())

    data: list[tuple[str, str]] = []

    for srv_rr in cast(RRset, srv_answer.rrset):
        logger.debug("ANSWER SRV: %r", srv_rr)

        try:
            host_answers = await resolver.resolve_name(
                srv_rr.target, lifetime=5, search=False
            )
        except NXDOMAIN:
            current_app.metric_dns_nxdomain_total.inc(
                {"qname": str(srv_rr.target), "rdtype": "AAAA/A"}
            )
            logger.warning("NXDOMAIN for %r", srv_rr.target)
            continue

        for address in host_answers.addresses():
            logger.debug("... address: %r", address)
            data.append((address, srv_rr.target.to_text(omit_final_dot=True)))

    # IP Address Lists formatting guidelines:
    # <https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-admin/policy/use-an-external-dynamic-list-in-policy/formatting-guidelines-for-an-external-dynamic-list/ip-address-list#idd44a975a-a94a-4398-864e-5cf223f1d351>
    content = ""
    for addr, comment in data:
        content += addr + "  " + comment
        content += "\r\n"

    resp = await make_response(content)
    resp.headers["Content-Type"] = "text/plain"
    return resp

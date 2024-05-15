from collections.abc import AsyncGenerator
import itertools
import logging

from dns.asyncresolver import Resolver
from dns.message import ADDITIONAL
from dns.rdatatype import AAAA, A, SRV
from dns.rdataclass import IN


logger = logging.getLogger(__name__)


async def query(qname: str) -> AsyncGenerator[tuple[str, str], None]:
    resolver = Resolver()

    srv_answer = await resolver.resolve(
        qname, SRV, raise_on_no_answer=True, lifetime=5, search=False
    )
    logger.debug("Response: %r", srv_answer.response.to_text())

    for srv_rr in srv_answer.rrset:
        logger.debug("ANSWER SRV: %r", srv_rr)

        additional_aaaa = (
            srv_answer.response.get_rrset(ADDITIONAL, srv_rr.target, IN, AAAA) or []
        )
        additional_a = (
            srv_answer.response.get_rrset(ADDITIONAL, srv_rr.target, IN, A) or []
        )

        for additional_rr in itertools.chain(additional_aaaa, additional_a):
            logger.debug(
                "... address from ADDITIONAL section: %r", additional_rr.address
            )
            yield additional_rr.address, srv_rr.target.to_text()

        if not additional_aaaa and not additional_a:
            logger.debug(
                "... addresses missing from ADDITIONAL section, querying separately"
            )
            host_answers = await resolver.resolve_name(
                srv_rr.target, raise_on_no_answer=False, lifetime=5, search=False
            )

            if not host_answers:
                logger.warning("NXDOMAIN for %r", srv_rr.target)
            else:
                for address in host_answers.addresses():
                    logger.debug("... address: %r", address)
                    yield address, srv_rr.target.to_text()

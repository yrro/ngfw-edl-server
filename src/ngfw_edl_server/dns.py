from collections.abc import AsyncGenerator
import logging

from dns.asyncresolver import Resolver


logger = logging.getLogger(__name__)


async def query(qname: str) -> AsyncGenerator[tuple[str, str], None]:
    resolver = Resolver()
    srv_answer = await resolver.resolve(
        qname, "srv", raise_on_no_answer=True, lifetime=5, search=False
    )
    logger.debug("Response: %r", srv_answer.response.to_text())
    for srv_rec in srv_answer:
        logger.debug("Answer RR: %r", srv_rec)
        host_answers = await resolver.resolve_name(
            srv_rec.target, raise_on_no_answer=True, lifetime=5, search=False
        )
        for address in host_answers.addresses():
            logger.debug("Address: %r", address)
            yield address, srv_rec.target.to_text()

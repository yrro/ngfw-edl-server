from typing import Iterable

from dns.resolver import Resolver


def query(qname: str) -> Iterable[tuple[str, str]]:
    resolver = Resolver()
    srv_answer = resolver.resolve(qname, "srv", raise_on_no_answer=True, lifetime=5, search=False)
    for srv_rec in srv_answer:
        host_answers = resolver.resolve_name(srv_rec.target, raise_on_no_answer=True, lifetime=5, search=False)
        for address in host_answers.addresses():
            yield address, srv_answer.name.to_text()


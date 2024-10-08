import pytest

from ngfw_edl_server import create_app


@pytest.fixture()
def dns_server():
    from dnslib.zoneresolver import ZoneResolver

    resolver = ZoneResolver(
        """
$ORIGIN normal.test.
_ldap._tcp SRV 0 100 389 server1.normal.test.
_ldap._tcp SRV 0 100 389 server2.normal.test.
server1 AAAA 2001:db8::1
server1    A 192.0.2.1
server2 AAAA 2001:db8::2
server2    A 192.0.2.2

$ORIGIN missing-service.test.
server3 AAAA 2001:db8::3
server3    A 192.0.2.3

$ORIGIN missing-address.test.
_ldap._tcp SRV 0 0 389 server4.missing-address.test.
_ldap._tcp SRV 0 0 389 server5.missing-address.test.
server4 AAAA 2001:db8::4
server4    A 192.0.2.4

$ORIGIN missing-addresses.test.
_ldap._tcp SRV 0 0 389 server6.missing-address.test.

$ORIGIN wrong-type.test.
_ldap._tcp AAAA ::
"""
    )
    from dnslib.server import DNSServer

    server = DNSServer(resolver, address="::1", port=0)
    server.start_thread()
    yield server
    server.stop()


@pytest.fixture()
def app(monkeypatch, dns_server):
    dns_server_port = dns_server.server.socket.getsockname()[1]
    print("DNS server on port %r", dns_server_port)

    monkeypatch.setenv("QUART_LOGGING_CONFIG__loggers__ngfw_edl_server__level", "DEBUG")

    app = create_app()
    app.config.update(
        {
            "DNSPYTHON_RESOLVER_PROPERTIES": {
                "port": dns_server_port,
                "nameservers": ["::1"],
            },
            "METRICS": False,
        }
    )
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.mark.asyncio
async def test_normal(dns_server, client):
    # when:
    response = await client.get("/srv/_ldap._tcp.normal.test")

    # then:
    assert 200 == response.status_code

    parsed_data = [line.split() for line in (await response.data).split(b"\r\n")]
    assert parsed_data.pop(-1) == []  # final terminator
    assert [
        [b"192.0.2.1", b"server1.normal.test"],
        [b"192.0.2.2", b"server2.normal.test"],
        [b"2001:db8::1", b"server1.normal.test"],
        [b"2001:db8::2", b"server2.normal.test"],
    ] == sorted(parsed_data)


@pytest.mark.asyncio
async def test_missing_service(dns_server, client):
    # when:
    response = await client.get("/srv/_ldap._tcp.missing-service.test")

    # then:
    assert 400 == response.status_code


@pytest.mark.asyncio
async def test_missing_address(dns_server, client):
    # when:
    response = await client.get("/srv/_ldap._tcp.missing-address.test")

    # then:
    assert 200 == response.status_code

    parsed_data = [line.split() for line in (await response.data).split(b"\r\n")]
    assert parsed_data.pop(-1) == []  # final terminator
    assert [
        [b"192.0.2.4", b"server4.missing-address.test"],
        [b"2001:db8::4", b"server4.missing-address.test"],
    ] == sorted(parsed_data)


@pytest.mark.asyncio
async def test_missing_addresses(dns_server, client):
    # when:
    response = await client.get("/srv/_ldap._tcp.missing-addresses.test")

    # then:
    assert 200 == response.status_code

    assert b"" == await response.data


@pytest.mark.asyncio
async def test_wrong_type(dns_server, client):
    # when:
    response = await client.get("/srv/_ldap._tcp.wrong-type.test")

    # then:
    assert 400 == response.status_code

    assert b"" == await response.data

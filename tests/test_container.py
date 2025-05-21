import logging
import os
import subprocess

import pytest
import requests
import trustme
import urllib3


pytestmark = pytest.mark.container

logger = logging.getLogger(__name__)


@pytest.fixture()
def session(ca):
    retries = urllib3.util.Retry(total=6, backoff_factor=0.1)
    sess = requests.Session()
    sess.mount("https://", requests.adapters.HTTPAdapter(max_retries=retries))
    with ca.cert_pem.tempfile() as ca_cert:
        sess.verify = ca_cert
        yield sess


@pytest.fixture(scope="session")
def ca():
    return trustme.CA()


@pytest.fixture(scope="session")
def container(ca, tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("tls")
    os.chmod(tmpdir, 0o755)
    server_cert = ca.issue_cert("localhost")
    server_cert.private_key_pem.write_to_path(tmpdir / "tls.key")
    server_cert.cert_chain_pems[0].write_to_path(tmpdir / "tls.crt")
    p = subprocess.run(
        [
            "podman",
            "run",
            "-d",
            "--pull=never",
            "--publish=127.0.0.1::8443",
            f"--volume={tmpdir}:/tmp/tls:ro,Z",
            "--env=NGFW_EDL_SERVER_LOG_LEVEL=DEBUG",
            "localhost/ngfw-edl-server",
            "-b",
            "0.0.0.0:8443",
            "--log-level=debug",
            "--certfile=/tmp/tls/tls.crt",
            "--key=/tmp/tls/tls.key",
        ],
        stdout=subprocess.PIPE,
        text=True,
    )
    if p.returncode != 0:
        pytest.fail("Couldn't start container")
    try:
        try:
            ctr = p.stdout.rstrip()
            p2 = subprocess.run(
                ["podman", "port", ctr, "8443/tcp"],
                stdout=subprocess.PIPE,
                text=True,
                check=True,
            )
            host, sep, port_ = p2.stdout.rstrip().partition(":")
            addr = (host, int(port_))
            yield addr
        finally:
            subprocess.run(["podman", "stop", ctr], check=True)

            p3 = subprocess.run(
                ["podman", "logs", ctr],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            logger.info("----- BEGIN CONTAINER LOGS ----")
            for line in p3.stdout.split("\n"):
                if line:
                    logger.info("%s", line)
            logger.info("----- END CONTAINER LOGS ----")

            p4 = subprocess.run(
                ["podman", "container", "inspect", ctr],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            logger.info("----- BEGIN CONTAINER INSPECT -----")
            for line in p4.stdout.split("\n"):
                if line:
                    logger.info("%s", line)
            logger.info("----- END CONTAINER INSPECT -----")

    finally:
        subprocess.run(["podman", "rm", "-f", ctr], check=True)


def test_metrics(container, session):
    # given:
    url = f"https://localhost:{container[1]}/metrics"

    # when:
    r = session.get(url, timeout=2)

    # then:
    r.raise_for_status()


def test_srv(container, session):
    # given:
    url = f"https://localhost:{container[1]}/srv/_ldap._tcp.demo1.freeipa.org"

    # when:
    r = session.get(url, timeout=2)

    # then:
    r.raise_for_status()

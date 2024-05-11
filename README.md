# fwdnsquery

Let's say you work in an Enterprise with a couple of common properties:

* Lots of sites
* A well known directory service built on top of somewhat open standards
* A well known Next-Generation Firewall

Your goal is to create firewall rules that allow traffic to the directory
servers. There are several servers per site, and servers and sites come and go
from time to time, so you can't simply create an 'address object' comprising a
hard coded list of IP addresses and call it a day.

Fortunately, the directory service makes it trivial for a client to discover
all of its servers by using [DNS
SRV](https://datatracker.ietf.org/doc/html/rfc2782) records. At the time of
writing, that's 28 years ago. So you'd think the Next-Generation Firewall,
designed as it is to meet the emerging needs of the most demanding Enterprises,
would be able to populate an address object with such queries, right?

Of course not, because what minority of enterprsies would need to be able to
create firewall rules that make it possible for clients to connect to the post
widely deployed directory service in existance? 🙄

Fortunately the Next-Generation Firewall has a second feature: external dynamic
lists. That is, it's able to fetch a list of IP addresses from a web server,
and rules are able to match on those IP addresses.

This project creates such external dynamic lists based on DNS queries for SRV
records.

## Example

Drag your Next Generation Firewall kicking and screaming into the incredible
future of 1996 by configuring an External Dynamic List with a URL such as:

    $ curl http://localhost:8080/edl/srv/_kerberos._udp.example.com
    2001:db8:20a:80::/64
    192.0.2.18/27
    2001:db8:30b:80::/64
    198.51.100.18/27
    2001:db8:50c:80::/64
    203.0.113.18/27

Flying cars are surely just around the corner!

## How to run

If you're into containers:

```
$ podman run --name=ngfw-edl-server --net=host --rm --replace ghcr.io/yrro/ngfw-edl-server --bind=0.0.0.0:8080
```

You can provide any desired [Gunicorn
settings](https://docs.gunicorn.org/en/latest/settings.html) as additional
arguments after the image name.

If you're not into containers, you need [Poetry](https://python-poetry.org/)
which will take care of creating a venv, installing dependencies, etc.

```
$ poetry install --only=main --extras=production

$ poetry run python -I -m gunicorn --bind=0.0.0.0:8080
```

## How to develop

Install development dependencies:

```
$ poetry install --with=dev
```

Run a development web server with debugger and hot code reloading:

```
$ poetry run python -m flask run --debug
```

Run the tests:

```
$ poetry run python -m pytest
```

... with coverage reports:

```
$ poetry run python -m pytest --cov --cov-report=html
```

## Before committing

Install [pre-commit](https://pre-commit.com/) and run `pre-commit install`;
this will configure your clone to run a variety of checks and you'll only be
able to commit if they pass.

If they don't work on your machine for some reason you can tell Git to let you
commit anyway with `git commit -n`.

## Building the container image

...

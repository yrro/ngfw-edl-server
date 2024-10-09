from importlib import metadata
import logging

from aioprometheus import Counter, Gauge, MetricsMiddleware
from aioprometheus.asgi.quart import metrics
from aioprometheus.collectors import Registry
from quart import Quart
from quart.typing import ResponseReturnValue

from . import server


def create_app() -> Quart:
    app = Quart(__name__)

    app.config.from_object(f"{__name__}.default_settings")
    app.config.from_prefixed_env()

    logging.config.dictConfig(app.config["LOGGING_CONFIG"])

    try:
        import logging_tree  # pylint: disable=import-outside-toplevel
    except ImportError:
        pass
    else:
        app.add_url_rule("/logging_config", "loging_config", logging_config)

    app.register_blueprint(server.blueprint)

    app.registry = Registry()  # isolate registries of multiple app instances
    app.asgi_app = MetricsMiddleware(app.asgi_app, registry=app.registry)
    app.add_url_rule(
        "/metrics", "metrics", metrics, methods=["GET"]
    )  # exports from app.registry

    Gauge(
        f"{__name__}_info",
        "Information about ngfw-edl-server",
        registry=app.registry,
    ).set(
        {
            "version": metadata.version("ngfw-edl-server"),
        },
        1,
    )

    app.metric_dns_nxdomain_total = Counter(
        f"{__name__}_dns_nxdomain_total",
        "Total NXDOMAIN reponses from DNS servers",
        registry=app.registry,
    )

    return app


async def logging_config() -> ResponseReturnValue:
    import logging_tree  # pylint: disable=import-outside-toplevel
    return logging_tree.format.build_description(), {"Content-Type": "text/plain"}

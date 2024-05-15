from importlib import metadata
import logging

from aioprometheus import Gauge, MetricsMiddleware
from aioprometheus.asgi.quart import metrics
from quart import Quart

from . import server


def create_app() -> Quart:
    app = Quart(__name__)

    app.config.from_object(f"{__name__}.default_settings")
    app.config.from_prefixed_env()

    logging.config.dictConfig(app.config["LOGGING_CONFIG"])

    if app.logger.isEnabledFor(logging.DEBUG):
        maybe_print_logging_config()

    app.register_blueprint(server.blueprint)

    app.asgi_app = MetricsMiddleware(app.asgi_app)
    app.add_url_rule("/metrics", "metrics", metrics, methods=["GET"])

    Gauge(
        f"{__name__}_info",
        "Information about ngfw-edl-server",
    ).set(
        {
            "version": metadata.version("ngfw-edl-server"),
        },
        1,
    )

    return app


def maybe_print_logging_config() -> None:
    try:
        from logging_tree import printout
    except ImportError:
        pass
    else:
        printout()

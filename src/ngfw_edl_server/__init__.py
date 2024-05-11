from importlib import metadata

from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics  # type: ignore [import-untyped]

from . import (
    log_config,
    server,
)


def create_app(host: log_config.Host | None = None) -> Flask:
    if host is None:
        host = log_config.Host.detect()

    host.configure_logging()

    app = Flask(__name__)

    #app.config.from_object(f"{__name__}.default_settings")
    #app.config.from_prefixed_env()

    app.register_blueprint(server.server)

    metrics = PrometheusMetrics(app)
    metrics.info(
        f"{__name__}_info",
        "Information about ngfw-edl-server",
        version=metadata.version("ngfw-edl-server"),
    )

    return app

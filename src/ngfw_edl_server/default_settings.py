import os

# To set the log level for messages emanating from the web application itself,
# use the NGFW_EDL_SERVER_LOG_LEVEL environment variable.
#
# To see debug messages from another logger "foo",, set its level with
# QUART_LOGGING_CONFIG__loggers__foo__level; to see all debug messages that
# propogate to the root logger, set the root logger level with
# QUART_LOGGING_CONFIG__root__level.
#
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(levelname)s:%(name)s:%(message)s",
        },
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "root": {
        "handlers": ["stderr"],
    },
    "loggers": {
        "ngfw_edl_server": {
            "level": os.environ.get("NGFW_EDL_SERVER_LOG_LEVEL", "WARNING"),
            "propogate": False,
            # Use the handler configured by Quart
        },
    },
}

# This file is used to configure gunicorn when running from the container
# image. As a result, a user can override any of these properties by providing
# additional arguments to the container.

bind = ["[::]:8080"]

accesslog = "-"

wsgi_app = "ngfw_edl_server:create_app()"

proc_name = "ngfw_edl_server"

worker_class = "uvicorn.workers.UvicornWorker"

# pylint: skip-file

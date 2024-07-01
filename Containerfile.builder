FROM registry.access.redhat.com/ubi9/ubi-minimal as builder

ARG PYTHON_SUFFIX

RUN \
  microdnf -y --nodocs --setopt=install_weak_deps=0 install \
    python${PYTHON_SUFFIX} \
    python${PYTHON_SUFFIX}-pip \
  && microdnf -y clean all

ENV PYTHONSAFEPATH=1

ENV PIP_ROOT_USER_ACTION=ignore

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python${PYTHON_SUFFIX} -m pip install poetry poetry-plugin-export

WORKDIR /opt/app-build

#
# Create the runtime virtual environment for the app.

RUN \
  python${PYTHON_SUFFIX} -m venv \
    --without-pip \
    /opt/app-root/venv

ENV PIP_PYTHON=/opt/app-root/venv/bin/python

#
# Install dependencies

RUN \
  python${PYTHON_SUFFIX} -m poetry \
    export \
      -f requirements.txt \
      -o requirements.txt \
      --only=main \
      -E production \
  && python${PYTHON_SUFFIX} -m pip \
    install \
      -r requirements.txt

#
# Build app and install

RUN \
  python${PYTHON_SUFFIX} -m poetry \
    build \
      -f wheel \
  && python${PYTHON_SUFFIX} -m pip \
    install \
      --no-deps \
      dist/*.whl

# vim: ts=8 sts=2 sw=2 et

# Bullseye for linux/amd64
FROM python:3.12-slim-bullseye@sha256:6fa552fb879325884b0c1b6792d14ae9500d246c8b19cc27876d84c7c41117ff AS base

RUN apt-get -qq update && apt-get -qqy install libpq-dev
RUN pip install --upgrade pip

WORKDIR /reko

COPY reko-0.0.1-py3-none-any.whl .

RUN pip install reko-0.0.1-py3-none-any.whl
RUN python -m compileall -q /usr/local/lib/python3.12/site-packages
RUN rm reko-0.0.1-py3-none-any.whl

ENV STATIC_ROOT=/reko/static
ENV MEDIA_ROOT=/reko/media

VOLUME ${STATIC_ROOT}
VOLUME ${MEDIA_ROOT}

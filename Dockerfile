FROM python:3.13-slim-bookworm@sha256:6c6b3c2deae72b980c4323738be824884c9a2e17588c93db82612f8a3072be88 AS base

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

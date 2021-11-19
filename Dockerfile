ARG venv_python=3.7

FROM python:${venv_python}-alpine3.13

LABEL Maintainer="CanDIG Project"

USER root

RUN apk update

RUN apk add --no-cache \
	autoconf \
	automake \
	bash \
	build-base \
	bzip2-dev \
	cargo \
	curl \
	curl-dev \
	gcc \
	git \
	libcurl \
	libffi-dev \
	libressl-dev \
	linux-headers \
	make \
	musl-dev \
	perl \
	postgresql-dev \
	postgresql-libs \
	xz-dev \
	yaml-dev \
	zlib-dev

RUN mkdir /app
WORKDIR /app
ADD ./requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app/chord_metadata_service

WORKDIR /app/chord_metadata_service


ENTRYPOINT ["python", "manage.py", "runserver"]
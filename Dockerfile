ARG venv_python=3.7

FROM python:${venv_python}-alpine3.13

<<<<<<< HEAD
LABEL Maintainer="CanDIG Project"
=======
LABEL Maintainer="CanDIG Team"
>>>>>>> a321c235d52b615aef2cf97393eb20214bed6707

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
<<<<<<< HEAD
=======
ADD ./requirements.txt /app
RUN pip install -r requirements.txt
>>>>>>> a321c235d52b615aef2cf97393eb20214bed6707

COPY . /app/chord_metadata_service

WORKDIR /app/chord_metadata_service
<<<<<<< HEAD
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "manage.py", "runserver"]
=======


ENTRYPOINT ["python", "manage.py", "runserver"]
>>>>>>> a321c235d52b615aef2cf97393eb20214bed6707

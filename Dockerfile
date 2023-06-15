ARG venv_python
ARG alpine_version
FROM python:${venv_python}-alpine${alpine_version}

LABEL Maintainer="CanDIG Team"
LABEL "candigv2"="chord_metadata_service"

USER root

RUN addgroup -S candig && adduser -S candig -G candig

RUN apk update

# Install the required packages for building Python packages with native extensions and PostgreSQL support
RUN apk add --no-cache bash build-base git postgresql-client postgresql-dev libffi-dev

RUN mkdir /app
WORKDIR /app
ADD ./requirements-candig-base.txt /app
ADD ./requirements-candig-dev.txt /app
RUN pip install --no-cache-dir -r requirements-candig-dev.txt

COPY . /app/chord_metadata_service

WORKDIR /app/chord_metadata_service

RUN chmod +x /app/chord_metadata_service/entrypoint.sh
CMD ["/app/chord_metadata_service/entrypoint.sh"]


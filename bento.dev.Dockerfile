FROM ghcr.io/bento-platform/bento_base_image:python-debian-2023.01.17

# Install Postgres client for checking if database is ready
RUN apt-get update -y && \
    apt-get install -y postgresql-client

# Backwards-compatible with old BentoV2 container layout
WORKDIR /app

COPY requirements.txt requirements.txt
COPY requirements-dev.txt requirements-dev.txt

# Install production dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Create temporary directory for downloading files etc.
RUN mkdir -p tmp

CMD [ "bash", "./entrypoint.dev.bash" ]

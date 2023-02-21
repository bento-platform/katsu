FROM ghcr.io/bento-platform/bento_base_image:python-debian-2023.02.21

# Install Postgres client for checking if database is ready
# Install Poetry for dependency management
RUN apt-get update -y && \
    apt-get install -y postgresql-client && \
    pip install --no-cache-dir "poetry==1.3.2"

# Backwards-compatible with old BentoV2 container layout
WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .
COPY poetry.toml .

# Install production + development dependencies
RUN poetry install --no-root

# Create temporary directory for downloading files etc.
RUN mkdir -p tmp

ENTRYPOINT [ "bash", "./entrypoint.bash" ]
CMD [ "bash", "./run.dev.bash" ]

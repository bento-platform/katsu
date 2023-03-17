FROM ghcr.io/bento-platform/bento_base_image:python-debian-2023.02.27

SHELL ["/bin/bash", "-c"]

# Install Postgres client for checking if database is ready
# Install Poetry for dependency management
#  - For development, install dependencies inside a venv so the developer can interact / change them
RUN apt-get update -y && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/* && \
    python -m venv /env && \
    source /env/bin/activate && \
    pip install --no-cache-dir "uvicorn[standard]==0.20.0"

# Backwards-compatible with old BentoV2 container layout
WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .
COPY poetry.toml .

# Install production + development dependencies
# Without --no-root, we get errors related to the code not being copied in yet.
# But we don't want the code here, otherwise Docker cache doesn't work well.
RUN source /env/bin/activate && poetry install --no-root

# Create temporary directory for downloading files etc.
RUN mkdir -p /app/tmp

# Copy in entrypoint and runner so we have some place to start even if the code doesn't get mounted in
COPY entrypoint.bash .
COPY run.dev.bash .

ENTRYPOINT [ "bash", "./entrypoint.bash" ]
CMD [ "bash", "./run.dev.bash" ]

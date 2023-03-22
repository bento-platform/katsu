FROM ghcr.io/bento-platform/bento_base_image:python-debian-2023.03.22

LABEL org.opencontainers.image.description="Local development image for Katsu."
LABEL devcontainer.metadata='[{ \
  "remoteUser": "bento_user", \
  "customizations": { \
    "vscode": { \
      "extensions": ["ms-python.python", "eamodio.gitlens"], \
      "settings": {"workspaceFolder": "/app"} \
    } \
  } \
}]'

SHELL ["/bin/bash", "-c"]

# Install Postgres client for checking if database is ready
# Install Poetry for dependency management
RUN apt-get update -y && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir "uvicorn[standard]==0.20.0"

# Backwards-compatible with old BentoV2 container layout
WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .
COPY poetry.toml .

# Install production + development dependencies
# Without --no-root, we get errors related to the code not being copied in yet.
# But we don't want the code here, otherwise Docker cache doesn't work well.
RUN poetry install --no-root

# Create temporary directory for downloading files etc.
RUN mkdir -p /app/tmp

# Copy in entrypoint and runner so we have some place to start even if the code doesn't get mounted in
COPY entrypoint.bash .
COPY run.dev.bash .

ENTRYPOINT [ "bash", "./entrypoint.bash" ]
CMD [ "bash", "./run.dev.bash" ]

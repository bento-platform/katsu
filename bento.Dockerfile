FROM ghcr.io/bento-platform/bento_base_image:python-debian-2024.02.14

SHELL ["/bin/bash", "-c"]

# Install Postgres client for checking if database is ready
# Install Poetry for dependency management and uvicorn to serve the API
RUN apt-get update -y && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir "uvicorn[standard]==0.27.1"

# Backwards-compatible with old BentoV2 container layout
WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .

# Install production dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --without dev

# Copy all application code
COPY . .

# Install Python package
RUN poetry install --without dev

# Create temporary directory for downloading files etc.
RUN mkdir -p tmp

ENTRYPOINT [ "bash", "./entrypoint.bash" ]
CMD [ "bash", "./run.bash" ]

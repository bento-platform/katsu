FROM ghcr.io/bento-platform/bento_base_image:python-debian-2025.01.21

SHELL ["/bin/bash", "-c"]

# - Install binutils, GDAL, PROJ, and GDAL for GeoDjango
# - Install Postgres client for checking if database is ready
RUN apt-get update -y && \
    apt-get install -y binutils gdal-bin libproj-dev gdal-bin postgresql-client && \
    rm -rf /var/lib/apt/lists/*

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

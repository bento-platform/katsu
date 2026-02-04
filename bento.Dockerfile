FROM ghcr.io/bento-platform/bento_base_image:python-debian-2026.01.14

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
    poetry install --no-root --without dev --no-cache --no-interaction

# Copy all application code
COPY chord_metadata_service chord_metadata_service
COPY entrypoint.bash .
COPY LICENSE .
COPY manage.py .
COPY README.md .
COPY run.bash .
COPY wait_for_db.bash .

# Install Python package
RUN poetry install --without dev --no-cache --no-interaction

# Uninstall build dependencies
RUN apt-get purge -y build-essential gcc git && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Create temporary directory for downloading files etc.
RUN mkdir -p tmp

ENTRYPOINT [ "bash", "./entrypoint.bash" ]
CMD [ "bash", "./run.bash" ]

FROM ghcr.io/bento-platform/bento_base_image:python-debian-latest

# Backwards-compatible with old BentoV2 container layout
WORKDIR /app

COPY requirements.txt requirements.txt
COPY requirements-dev.txt requirements-dev.txt

# Install production dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy all application code
COPY . .

# Create temporary directory for downloading files etc.
RUN mkdir -p tmp

CMD [ "sh", "./entrypoint.dev.sh" ]

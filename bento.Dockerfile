FROM ghcr.io/bento-platform/bento_base_image:python-debian-latest

RUN pip install --no-cache-dir "hypercorn[uvloop]==0.14.3"

# Backwards-compatible with old BentoV2 container layout
WORKDIR /app

COPY requirements.txt requirements.txt

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Create temporary directory for downloading files etc.
RUN mkdir -p tmp

CMD [ "sh", "./entrypoint.sh" ]

#!/bin/bash

# Wait for database to start
./wait_for_db.bash

# Run migrations; make migrations for other apps if needed
python manage.py makemigrations admin auth
python manage.py migrate

# Set the internal port unless it's been externally configured
if [ -z "${INTERNAL_PORT}" ]; then
  # Set default internal port to 8000
  INTERNAL_PORT=8000
fi

# Run the ASGI server
uvicorn chord_metadata_service.metadata.asgi:application \
  --workers 1 \
  --loop uvloop \
  --host "0.0.0.0" \
  --port "${INTERNAL_PORT}"

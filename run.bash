#!/bin/bash

# Wait for database to start
./wait_for_db.bash

# Run migrations; make migrations for other apps if needed
python manage.py makemigrations admin auth
python manage.py migrate

# Set default internal port to 8000
: "${INTERNAL_PORT:=8000}"

# Run the ASGI server
uvicorn chord_metadata_service.metadata.asgi:application \
  --workers 1 \
  --loop uvloop \
  --host "0.0.0.0" \
  --port "${INTERNAL_PORT}"

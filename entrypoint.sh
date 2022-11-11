#!/bin/sh

if [ -z "${INTERNAL_PORT}" ]; then
  # Set default internal port to 8000
  INTERNAL_PORT=8000
fi

# Run migrations; make migrations for other apps if needed
python manage.py makemigrations
python manage.py migrate

hypercorn chord_metadata_service.metadata.asgi:application \
  --workers 1 \
  --worker_class uvloop \
  --bind "0.0.0.0:${INTERNAL_PORT}"

#!/bin/bash

# Install the package / any dependency changes
poetry install

# Wait for database to start
./wait_for_db.bash

# Run migrations; make migrations for other apps if needed
python manage.py makemigrations
python manage.py migrate

# Set the internal port unless it's been externally configured
if [ -z "${INTERNAL_PORT}" ]; then
  # Set default internal port to 8000
  INTERNAL_PORT=8000
fi

python manage.py runserver "0.0.0.0:${INTERNAL_PORT}"

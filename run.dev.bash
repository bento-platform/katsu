#!/bin/bash

# Set .gitconfig for development
/set_gitconfig.bash

# Source the development virtual environment
source /env/bin/activate

# Update dependencies and install module locally (similar to pip install -e: "editable mode")
poetry install

# Wait for database to start
./wait_for_db.bash

# Run migrations; make migrations for other apps if needed
python manage.py makemigrations
python manage.py migrate

# Set the internal port unless it's been externally configured
if [[ -z "${INTERNAL_PORT}" ]]; then
  # Set default internal port to 8000
  INTERNAL_PORT=8000
fi

python manage.py runserver "0.0.0.0:${INTERNAL_PORT}"

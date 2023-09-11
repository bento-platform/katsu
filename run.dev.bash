#!/bin/bash

# Set .gitconfig for development
/set_gitconfig.bash

# Update dependencies and install module locally
/poetry_user_install_dev.bash

# Wait for database to start
./wait_for_db.bash

# Run migrations; make migrations for admin/auth built-in apps if needed
python manage.py makemigrations admin auth
python manage.py migrate

# Set default internal port to 8000
: "${INTERNAL_PORT:=8000}"

python manage.py runserver "0.0.0.0:${INTERNAL_PORT}"

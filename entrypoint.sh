#!/bin/bash

set -e

# Wait for the database to be ready
until pg_isready -h metadata-db -p 5432 -U admin; do
  echo "Waiting for the database to be ready..."
  sleep 1
done

# Run migrations and start the server
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

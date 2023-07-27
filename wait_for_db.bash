#!/bin/bash

PGPASSWORD="${POSTGRES_PASSWORD}"
if [[ -n "${POSTGRES_PASSWORD_FILE}" ]]; then
  PGPASSWORD="$(cat "${POSTGRES_PASSWORD_FILE}")"
fi
export PGPASSWORD

# Check if we have a 0-length password; if so, output a warning
if [[ -z "${PGPASSWORD}" ]]; then
  >&2 echo "Warning: 0-length POSTGRES_PASSWORD. Make sure POSTGRES_PASSWORD / BENTOV2_KATSU_DB_PASSWORD is set!"
fi

# Set default values for Postgres connection variables
: "${POSTGRES_DATABASE:=metadata}"
: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_USER:=admin}"

until \
  echo "Checking for Postgres on postgresql://${POSTGRES_USER}:[redacted]@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DATABASE}"
  pg_isready \
  -d "${POSTGRES_DATABASE}" \
  -h "${POSTGRES_HOST}" \
  -p "${POSTGRES_PORT}" \
  -U "${POSTGRES_USER}"
do
  echo "Waiting 2 seconds for database host..."
  sleep 2
done

unset PGPASSWORD

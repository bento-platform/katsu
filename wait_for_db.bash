#!/bin/bash

PGPASSWORD="${POSTGRES_PASSWORD}"
if [[ -n "${POSTGRES_PASSWORD_FILE}" ]]; then
  PGPASSWORD="$(cat "${POSTGRES_PASSWORD_FILE}")"
fi
export PGPASSWORD

until \
  pg_isready \
  -d "${POSTGRES_DATABASE:-metadata}" \
  -h "${POSTGRES_HOST:-localhost}" \
  -p "${POSTGRES_PORT:-5432}" \
  -U "${POSTGRES_USER:-admin}"
do
  echo "Waiting 2 seconds for database host..."
  sleep 2
done

unset PGPASSWORD

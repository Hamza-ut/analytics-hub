#!/bin/sh

# set -e: Exit immediately if a command exits with a non-zero status.
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

# on second run "|| true" will prevent the script from exiting if the superuser already exists
echo "Ensuring superuser exists..."
python manage.py createsuperuser --noinput || true

# 4. Hand control to the CMD from the Dockerfile (Gunicorn)
echo "Handing control over to the server command..."
exec "$@"
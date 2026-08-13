#!/bin/sh

# set -e: Exit immediately if a command exits with a non-zero status.
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Ensuring superuser exists..."
python manage.py createsuperuser --noinput || true

echo "Seeding workflows..."
python manage.py ensure_workflows

# Hand control to the CMD from the Dockerfile (Gunicorn or runserver)
echo "Handing control over to the server command..."
exec "$@"
#!/bin/sh

# 1. Gather all CSS/JS assets into your static root folder for production
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 2. Look at the database and safely apply any missing tables/columns
echo "Applying database migrations..."
python manage.py migrate --noinput

# 3. Automatically create the superuser if it doesn't exist
echo "Ensuring superuser exists..."
python manage.py createsuperuser --noinput || true

# 4. Hand control to the CMD from the Dockerfile (Gunicorn)
echo "Starting Gunicorn server..."
exec "$@"
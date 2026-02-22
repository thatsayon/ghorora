#!/bin/sh

set -e

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 0.5
done
echo "PostgreSQL is ready."

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

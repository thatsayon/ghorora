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

echo "Starting Uvicorn..."
exec uvicorn config.asgi:application \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 3 \
    --access-log

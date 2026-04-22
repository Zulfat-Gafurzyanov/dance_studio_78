#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting server..."
exec gunicorn main:app \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:8000 \
    -w 4 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -

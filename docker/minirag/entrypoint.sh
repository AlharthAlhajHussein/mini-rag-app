#!/bin/bash
set -e

echo "Running database migrations..."
# alembic -c /app/models/db_schemes/minirag/alembic.ini upgrade head
# echo "Migrations complete. Starting FastAPI..."

cd /app/models/db_schemes/minirag/
alembic upgrade head
cd /app
exec "$@"

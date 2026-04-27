#!/bin/sh
set -e

echo "⏳ Waiting for database..."
while ! python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(os.environ.get('DATABASE_URL', ''))
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    sleep 1
done
echo "✅ Database is ready."

echo "📦 Running migrations..."
alembic upgrade head

echo "🚀 Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

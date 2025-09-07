#!/usr/bin/env bash
set -e

echo "⏳ Wachten tot database beschikbaar is..."

python - <<'PY'
import os, time, sys
import psycopg

db = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST","db"),
    "port": int(os.getenv("POSTGRES_PORT","5432")),
}

for i in range(30):  # max 30 × 2s = 1 minuut
    try:
        with psycopg.connect(connect_timeout=3, **db) as _:
            print("✅ Database bereikbaar.")
            break
    except Exception:
        time.sleep(2)
else:
    print("❌ Database niet bereikbaar, stop script.", file=sys.stderr)
    sys.exit(1)
PY

echo "🚀 Migraties uitvoeren..."
python manage.py migrate --noinput || true

echo "🌐 Start Django dev-server..."
exec python manage.py runserver 0.0.0.0:8000

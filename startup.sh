#!/usr/bin/env bash
set -e

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
for i in range(90):
    try:
        with psycopg.connect(connect_timeout=3, **db) as _:
            break
    except Exception as e:
        time.sleep(2)
else:
    print("Database niet bereikbaar.", file=sys.stderr)
    sys.exit(1)
PY

# Migrate + static (in dev laten we collectstatic achterwege)
python manage.py migrate --noinput || true

if [ "${DJANGO_DEBUG:-1}" = "0" ]; then
  python manage.py collectstatic --noinput || true
  exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
else
  exec python manage.py runserver 0.0.0.0:8000
fi

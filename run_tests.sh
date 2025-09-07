#!/bin/bash
set -e

echo "=== Backup maken voor veiligheid ==="
wr backup --name pre-tests

echo "=== Django checks uitvoeren ==="
docker compose exec -T web python manage.py check

echo "=== Migrations checken ==="
docker compose exec -T web python manage.py makemigrations --check --dry-run

echo "=== Database migreren ==="
docker compose exec -T web python manage.py migrate

echo "=== Collect static ==="
docker compose exec -T web python manage.py collectstatic --noinput || true

echo "=== Testen draaien met pytest ==="
docker compose exec -T web pytest -v --maxfail=3 --disable-warnings

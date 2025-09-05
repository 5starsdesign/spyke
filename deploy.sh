#!/bin/bash
set -e

# Load DB credentials from .env
export $(grep -E '^(POSTGRES_DB|POSTGRES_USER|POSTGRES_PASSWORD)=' .env | xargs)

TS=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/bakkie-op/live
mkdir -p "$BACKUP_DIR"

echo "▶️ Live deploy gestart..."

echo "▶️ Code + DB backup maken..."
tar -czf "$BACKUP_DIR/woningruil_${TS}.tgz" -C /srv woningruil
docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_DIR/db_${TS}.sql"

echo "▶️ Containers bouwen en starten..."
docker compose up -d --build

echo "▶️ Migraties draaien..."
docker compose exec -T web python manage.py migrate

echo "▶️ Staticfiles verzamelen..."
docker compose exec -T web python manage.py collectstatic --noinput || true

echo "✅ Live deploy voltooid!"

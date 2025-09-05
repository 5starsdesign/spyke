#!/bin/bash
set -e

# Load DB credentials from .env
export $(grep -E '^(POSTGRES_DB|POSTGRES_USER|POSTGRES_PASSWORD)=' .env | xargs)

BACKUP_DIR=~/bakkie-op/live
TS=$(date +%Y%m%d_%H%M%S)

echo "▶️ Live rollback gestart..."

LATEST_TGZ=$(ls -t ${BACKUP_DIR}/woningruil_*.tgz 2>/dev/null | head -n1)
LATEST_DB=$(ls -t ${BACKUP_DIR}/db_*.sql 2>/dev/null | head -n1)

if [ -z "$LATEST_TGZ" ] || [ -z "$LATEST_DB" ]; then
  echo "❌ Geen complete backup gevonden in $BACKUP_DIR"
  exit 1
fi

echo "▶️ Herstellen van code uit $LATEST_TGZ ..."
tar -xzf "$LATEST_TGZ" -C /srv

echo "▶️ Database herstellen vanuit $LATEST_DB ..."
cat "$LATEST_DB" | docker compose exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"

echo "✅ Rollback voltooid op $(date)"

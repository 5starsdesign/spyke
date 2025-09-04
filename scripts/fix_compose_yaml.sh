#!/usr/bin/env bash
set -euo pipefail
cd "${HOME}/woningruil"

FILE="docker-compose.yml"
cp -a "$FILE" "${FILE}.bak.$(date +%s)"

# Normaliseer: tabs -> spaties, CRLF -> LF
sed -i 's/\t/  /g' "$FILE"
sed -i 's/\r$//' "$FILE"

# Verwijder fout blok na 'volumes: pgdata'
awk '
  BEGIN{in_bad=0}
  {
    if ($0 ~ /^[[:space:]]*volumes:[[:space:]]*$/) {seen_vol=1}
    if (seen_vol && $0 ~ /^[[:space:]]*pgdata:[[:space:]]*null[[:space:]]*$/) {print; next}
    if (seen_vol && $0 ~ /^[[:space:]]*environment:[[:space:]]*$/) {in_bad=1; next}
    if (in_bad) {
      if ($0 ~ /^[^[:space:]]/ || $0 ~ /^[[:space:]]*[a-zA-Z0-9_]+:/) {in_bad=0}
      else {next}
    }
    print
  }
' "$FILE" > "$FILE.tmp" && mv "$FILE.tmp" "$FILE"

# Valideer
docker compose config >/dev/null

# Herstart kort
docker compose up -d --build
docker compose exec -T web python manage.py collectstatic --noinput || true

echo "Compose hersteld."

#!/bin/bash
set -e

echo "== Django Routes Sanity Check =="

# alle urls ophalen
ALL_URLS=$(docker compose exec -T web python manage.py show_urls | awk '{print $1}')

# verwachtte routes
EXPECTED=(
  "/" 
  "/ruilwoningen/"
  "/huurwoningen/"
  "/koopwoningen/"
  "/woningen/huur/<slug>/"
  "/woningen/koop/<slug>/"
  "/woningen/ruil/<slug>/"
  "/accounts/"
  "/dash/member/"
  "/dash/agency/mijn/"
  "/dash/agency/<slug>/bewerken/"
)

# checken
for route in "${EXPECTED[@]}"; do
  echo -n "Check $route ... "
  echo "$ALL_URLS" | grep -q "$route" && echo "OK" || echo "❌ MISSING"
done

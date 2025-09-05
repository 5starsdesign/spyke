#!/bin/bash
set -euo pipefail

failok() { "$@" || true; }

check_url () {
  local url=$1
  echo "→ $url"
  failok curl -kIs "$url" | head -n 1
}

echo "== Docker status =="
docker compose ps
docker compose logs -n 20 web

echo "== Prod checks =="
check_url "http://127.0.0.1:8000/"
check_url "https://123woningruilen.nl/"
check_url "https://123woningruilen.nl/static/admin/css/base.css"
check_url "https://123woningruilen.nl/admin/"

echo "== Staging checks =="
check_url "http://127.0.0.1:8001/"
check_url "https://staging.123woningruilen.nl/"
check_url "https://staging.123woningruilen.nl/static/admin/css/base.css"
check_url "https://staging.123woningruilen.nl/admin/"

cat >> sanity.sh <<'EOF'

echo "== Extra checks =="

# Publieke routes
check_url "https://123woningruilen.nl/"
check_url "https://123woningruilen.nl/ruilwoningen/"
check_url "https://123woningruilen.nl/huurwoningen/"
check_url "https://123woningruilen.nl/koopwoningen/"

# Detailpagina voorbeelden (redirect naar login/signup is ok)
check_url "https://123woningruilen.nl/woningen/huur/test-slug/"
check_url "https://123woningruilen.nl/woningen/koop/test-slug/"
check_url "https://123woningruilen.nl/woningen/ruil/test-slug/"

# Accounts
check_url "https://123woningruilen.nl/accounts/login/"
check_url "https://123woningruilen.nl/accounts/signup/"

# Dashboards
check_url "https://123woningruilen.nl/dash/"
check_url "https://123woningruilen.nl/dash/agency/mijn/"
check_url "https://123woningruilen.nl/dash/agency/test-slug/bewerken/"

# Staging idem
check_url "https://staging.123woningruilen.nl/ruilwoningen/"
check_url "https://staging.123woningruilen.nl/huurwoningen/"
check_url "https://staging.123woningruilen.nl/koopwoningen/"
check_url "https://staging.123woningruilen.nl/accounts/login/"
check_url "https://staging.123woningruilen.nl/dash/"
EOF

echo "== Extra checks =="

# Publieke routes
check_url "https://123woningruilen.nl/"
check_url "https://123woningruilen.nl/ruilwoningen/"
check_url "https://123woningruilen.nl/huurwoningen/"
check_url "https://123woningruilen.nl/koopwoningen/"

# Detailpagina voorbeelden (redirect naar login/signup is ok)
check_url "https://123woningruilen.nl/woningen/huur/test-slug/"
check_url "https://123woningruilen.nl/woningen/koop/test-slug/"
check_url "https://123woningruilen.nl/woningen/ruil/test-slug/"

# Accounts
check_url "https://123woningruilen.nl/accounts/login/"
check_url "https://123woningruilen.nl/accounts/signup/"

# Dashboards
check_url "https://123woningruilen.nl/dash/"
check_url "https://123woningruilen.nl/dash/agency/mijn/"
check_url "https://123woningruilen.nl/dash/agency/test-slug/bewerken/"

# Staging idem
check_url "https://staging.123woningruilen.nl/ruilwoningen/"
check_url "https://staging.123woningruilen.nl/huurwoningen/"
check_url "https://staging.123woningruilen.nl/koopwoningen/"
check_url "https://staging.123woningruilen.nl/accounts/login/"
check_url "https://staging.123woningruilen.nl/dash/"

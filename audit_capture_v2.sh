#!/usr/bin/env bash
set -euo pipefail
ts="$(date +%Y%m%d_%H%M%S)"
mkdir -p audits
LOG="audits/audit_${ts}.txt"
run(){ echo -e "\n▶ $*" | tee -a "$LOG"; (eval "$*" 2>&1 | tee -a "$LOG"); }

run "docker compose up -d --build"
run "docker compose exec -T web python manage.py makemigrations --check --dry-run || true"
run "docker compose exec -T web python manage.py migrate"
run "docker compose exec -T web python manage.py showmigrations"
run "docker compose exec -T web python manage.py check --fail-level ERROR"
run "docker compose exec -T web python manage.py check --deploy || true"
run "docker compose exec -T web python manage.py collectstatic --noinput || true"

run "docker compose exec -T web bash -lc 'python manage.py shell <<\"PY\"
from django.test import Client
from django.urls import get_resolver, reverse, NoReverseMatch

paths = [\"/\",\"/ruilwoningen/\",\"/huurwoningen/\",\"/koopwoningen/\",
         \"/accounts/\",\"/accounts/login/\",\"/accounts/signup/\",
         \"/dash/member/eigen/\",\"/dash/member/wens/\",
         \"/dash/agency/mijn/\",\"/dash/agency/nieuw/\"]

resolver = get_resolver()
for name in sorted(k for k in resolver.reverse_dict.keys() if isinstance(k,str)):
    try:
        url = reverse(name)
        if url not in paths: paths.append(url)
    except NoReverseMatch:
        pass

client = Client()
print(\"== Route smoke test (HTTP_HOST=localhost) ==\")
ok = {200,301,302}
for p in paths:
    try:
        r = client.get(p, HTTP_HOST=\"localhost\")
        status = \"PASS\" if r.status_code in ok else (\"WARN\" if r.status_code<500 else \"FAIL\")
        print(f\"{status:4} {r.status_code:3}  {p}\")
    except Exception as e:
        print(f\"FAIL EXC   {p}  {e}\")

print(\"\\n== Modelvelden ==\")
def fields(model): return \", \".join(sorted(f.name for f in model._meta.fields))
try:
    from properties.models import MarketListing
    print(\"MarketListing:\", fields(MarketListing))
except Exception as e:
    print(\"MarketListing: ERROR:\", e)
try:
    from properties.models import ExchangeOffer
    print(\"ExchangeOffer:\", fields(ExchangeOffer))
except Exception as e:
    print(\"ExchangeOffer: ERROR:\", e)
PY'"

echo -e "\n✅ Audit klaar. Log: $LOG"

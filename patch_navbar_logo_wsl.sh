#!/usr/bin/env bash
set -euo pipefail

# Update layout(s): voeg {% static %} toe en toon logo in navbar-brand
for T in templates/_layout.html templates/base.html templates/layout.html; do
  [ -f "$T" ] || continue
  sed -i 's/\r$//' "$T"
  grep -q "{% load static %}" "$T" || sed -i '1s/^/{% load static %}\n/' "$T"
  python3 - "$T" <<'PY'
import io,re,sys
p=sys.argv[1]; s=io.open(p,encoding='utf-8').read()
# normaliseer hard pad naar static-tag
s = s.replace('/static/img/logo.svg', "{% static 'img/logo.svg' %}")
# zorg dat <a class="navbar-brand"> een logo <img> bevat
m = re.search(r'(<a class="navbar-brand[^>]*>)([\s\S]*?)(</a>)', s)
if m:
    inner = m.group(2)
    if 'logo.svg' not in inner:
        new = m.group(1) + '<img src="{% static \'img/logo.svg\' %}" alt="Logo" height="28" class="me-2 align-text-bottom">Woningruil' + m.group(3)
        s = s[:m.start()] + new + s[m.end():]
io.open(p,'w',encoding='utf-8').write(s)
print("patched", p)
PY
done

# Placeholder logo (alleen aanmaken als het niet bestaat)
mkdir -p static/img
if [ ! -f static/img/logo.svg ]; then
cat > static/img/logo.svg <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="180" height="48" viewBox="0 0 180 48" role="img" aria-label="Woningruil">
  <rect width="180" height="48" rx="8" fill="#0d6efd"/>
  <circle cx="24" cy="24" r="12" fill="#ffffff"/>
  <path d="M24 12 L34 22 L32 24 L24 16 L16 24 L14 22 Z" fill="#0d6efd"/>
  <text x="52" y="30" font-family="system-ui, -apple-system, Segoe UI, Roboto, Arial" font-size="18" fill="#ffffff" font-weight="700">Woningruil</text>
</svg>
SVG
fi

# Build + static
docker compose up -d --build
docker compose exec -T web python manage.py collectstatic --noinput || true
echo "✅ Navbar toont logo. Vervang later static/img/logo.svg door jouw eigen logo."

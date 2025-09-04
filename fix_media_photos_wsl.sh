#!/usr/bin/env bash
set -euo pipefail

# CRLF→LF helper
fixlf(){ [ -f "$1" ] && sed -i 's/\r$//' "$1" || true; }

# --- settings.py: MEDIA ---
S="config/settings.py"
if [ -f "$S" ]; then
  fixlf "$S"
  grep -q "MEDIA_URL" "$S" || cat >> "$S" <<'PY'

# === Media (dev) ===
from pathlib import Path as _Path  # safe import
try:
    BASE_DIR
except NameError:
    BASE_DIR = _Path(__file__).resolve().parent.parent
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
PY
fi

# --- urls.py: serve media in dev ---
U="config/urls.py"
if [ -f "$U" ]; then
  fixlf "$U"
  grep -q "from django.conf import settings" "$U" || sed -i '1s/^/from django.conf import settings\n/' "$U"
  grep -q "from django.conf.urls.static import static" "$U" || sed -i '1s/^/from django.conf.urls.static import static\n/' "$U"
  grep -q "static(settings.MEDIA_URL" "$U" || echo 'urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)' >> "$U"
fi

# --- docker-compose: media volume ---
DC="docker-compose.yml"
if [ -f "$DC" ]; then
  fixlf "$DC"
  # voeg ./media mount toe bij service "web" indien ontbreekt
  python3 - "$DC" <<'PY'
import io,sys,re,yaml
p=sys.argv[1]; s=io.open(p,encoding='utf-8').read()
try:
    data=yaml.safe_load(s)
except Exception:
    print("! kon docker-compose niet parsen, sla deze stap over"); sys.exit(0)
web = (data.get('services') or {}).get('web')
if web is not None:
    vols = web.get('volumes') or []
    if './media:/app/media' not in vols:
        vols.append('./media:/app/media')
        web['volumes']=vols
        data['services']['web']=web
        io.open(p,'w',encoding='utf-8').write(yaml.dump(data, sort_keys=False))
        print("compose: media-volume toegevoegd")
PY
fi

# --- placeholder + map ---
mkdir -p static/img media
if [ ! -f static/img/placeholder_listing.svg ]; then
cat > static/img/placeholder_listing.svg <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
  <rect width="640" height="360" fill="#e9ecef"/>
  <g fill="none" stroke="#adb5bd" stroke-width="4">
    <rect x="40" y="60" width="560" height="240" rx="12"/>
    <path d="M100 240l80-80 70 70 90-90 120 120"/>
  </g>
</svg>
SVG
fi

# --- models.py: cover_url helper ---
M="properties/models.py"
if [ -f "$M" ]; then
  fixlf "$M"
  # import static()
  grep -q "from django.templatetags.static import static" "$M" || sed -i '1s/^/from django.templatetags.static import static\n/' "$M"
  # voeg cover_url property toe als die er nog niet is
  python3 - "$M" <<'PY'
import io,re,sys
p=sys.argv[1]; s=io.open(p,encoding='utf-8').read()
# vind MarketListing class
cls = re.search(r'class\s+MarketListing\([^)]*\):', s)
if cls and 'def cover_url(self):' not in s:
    insert = """

    @property
    def cover_url(self):
        img = self.images.first()
        try:
            return img.image.url if img and getattr(img, "image", None) else static('img/placeholder_listing.svg')
        except Exception:
            return static('img/placeholder_listing.svg')
"""
    # plaats voor einde class (voor volgende class of EOF)
    tail = s[cls.end():]
    nxt = re.search(r'\nclass\s+\w+', tail)
    end = cls.end() + (nxt.start() if nxt else len(tail))
    s = s[:end] + insert + s[end:]
    io.open(p,'w',encoding='utf-8').write(s)
    print("cover_url toegevoegd aan MarketListing")
PY
fi

# --- rebuild + collectstatic ---
docker compose up -d --build
docker compose exec -T web python manage.py collectstatic --noinput || true
docker compose exec -T web python manage.py check || true

echo "✅ Media ingesteld. Uploads staan in ./media en {{ listing.cover_url }} werkt als fallback."

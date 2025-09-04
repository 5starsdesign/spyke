from django.shortcuts import render, get_object_or_404
from accounts.models import Profile
from .models import MarketListing, ExchangeOffer
def market_detail(request, slug, kind):
    obj = get_object_or_404(MarketListing, slug=slug, listing_kind=kind, is_published=True)
    can_view_contact = False
    if request.user.is_authenticated:
        prof = getattr(request.user, "profile", None)
        can_view_contact = bool(prof and prof.is_premium) or request.user == obj.owner or request.user.is_staff
    return render(request, "public/market_detail.html", {"obj": obj, "can_view_contact": can_view_contact})
def exchange_detail(request, pk):
    obj = get_object_or_404(ExchangeOffer, pk=pk, is_published=True)
    can_view_contact = request.user.is_authenticated
    return render(request, "public/exchange_detail.html", {"obj": obj, "can_view_contact": can_view_contact})



def _is_premium(user):
    try:
        prof = getattr(user, "profile", None)
        return bool(getattr(prof, "is_premium", False))
    except Exception:
        return False

from django.http import JsonResponse
from django.db.models import Q


from django.http import JsonResponse
from django.db.models import Q

def _thumb_url(obj):
    for attr in ["cover","image","photo","main_photo","main_image","thumbnail","thumb","foto"]:
        if hasattr(obj, attr):
            try:
                f = getattr(obj, attr)
                if f:
                    return getattr(f, "url", "") or ""
            except Exception:
                pass
    for rel in ["photos","images","fotos"]:
        if hasattr(obj, rel):
            try:
                p = getattr(obj, rel).all().first()
                if p:
                    for a in ["image","photo","file","thumb"]:
                        if hasattr(p, a):
                            f = getattr(p, a)
                            return getattr(f, "url", "") or ""
            except Exception:
                pass
    return ""

def ads_json(request):
    n = int(request.GET.get("n", 6))
    items = []
    try:
        from .models import Listing
        qs = Listing.objects.all()
        # voorkeur: makelaars en huizenbezitters
        try:
            from accounts.models import Profile
            qs_pref = qs.filter(
                owner__profile__role__in=[getattr(Profile,"ROLE_AGENCY","AGENCY"),
                                          getattr(Profile,"ROLE_OWNER","OWNER")]
            )
            qs = qs_pref if qs_pref.exists() else qs
        except Exception:
            pass
        # alleen HUUR/KOOP (nooit RUIL)
        try:
            qs = qs.exclude(listing_kind__iexact="RUIL")
            qs = qs.filter(listing_kind__isnull=False)
            qs = qs.filter(listing_kind__in=["HUUR","KOOP"])
        except Exception:
            # als veld ontbreekt, filteren we later in Python
            pass

        qs = qs.order_by("?")

        for o in qs:
            kind = (getattr(o, "listing_kind", "") or "").upper()
            if kind == "RUIL":
                continue
            if kind and kind not in ("HUUR","KOOP"):
                continue
            slug = getattr(o, "slug", None)
            if slug:
                url = f"/woningen/huur/{slug}/" if kind=="HUUR" else f"/woningen/koop/{slug}/"
            else:
                url = "#"
            items.append({
                "title": getattr(o, "title", "Woning"),
                "city": getattr(o, "city", "") or "",
                "kind": kind or "",
                "url": url,
                "thumb": _thumb_url(o),
            })
            if len(items) >= n:
                break
    except Exception:
        items = []

    # Fallback: placeholders HUUR/KOOP (nooit RUIL)
    if not items:
        cities = ["Amsterdam","Rotterdam","Utrecht","Den Haag","Eindhoven","Groningen","Zwolle","Nijmegen"]
        ph = []
        for i in range(n):
            kind = "HUUR" if i % 2 == 0 else "KOOP"
            ph.append({
                "title": "Huurwoning — 3 kamers" if kind=="HUUR" else "Koopwoning — gezinswoning",
                "city": cities[i % len(cities)],
                "kind": kind,
                "url": "#",
                "thumb": f"/static/img/ads/{'huur' if kind=='HUUR' else 'koop'}.svg",
            })
        items = ph

    return JsonResponse({"items": items})

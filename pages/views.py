from django.shortcuts import get_object_or_404, render

from accounts.models import Profile
from properties.models import ExchangeOffer, MarketListing


def home(request):
    featured = MarketListing.objects.filter(is_published=True).order_by(
        "-is_featured", "-created_at"
    )[:8]
    return render(request, "home.html", {"featured": featured})


def ruil_list(request):
    q = ExchangeOffer.objects.filter(is_published=True).order_by("-created_at")
    return render(request, "public/ruil_list.html", {"items": q})


def huur_list(request):
    q = MarketListing.objects.filter(
        is_published=True, listing_kind=MarketListing.K_HUUR
    ).order_by("-created_at")
    return render(request, "public/huur_list.html", {"items": q})


def koop_list(request):
    q = MarketListing.objects.filter(
        is_published=True, listing_kind=MarketListing.K_KOOP
    ).order_by("-created_at")
    return render(request, "public/koop_list.html", {"items": q})


def agency_public(request, slug):
    prof = get_object_or_404(Profile, slug=slug, role=Profile.ROLE_AGENCY)
    listings = prof.user.marketlisting_set.all().filter(is_published=True)
    return render(request, "public/agency.html", {"profile": prof, "items": listings})

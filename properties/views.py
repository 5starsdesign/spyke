from django.shortcuts import get_object_or_404, render
from .models import ExchangeOffer, MarketListing
from accounts.models import Profile


def exchange_detail(request, pk):
    offer = get_object_or_404(ExchangeOffer, pk=pk)
    profile = None
    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)

    # Paywall: niet-premium → blur
    show_full = profile and profile.is_premium

    return render(
        request,
        "properties/exchangeoffer_detail.html",
        {"offer": offer, "show_full": show_full, "paywall": True},
    )


def market_detail(request, slug, kind=None):
    listing = get_object_or_404(MarketListing, slug=slug)
    # Koop- en huurwoningen → altijd alles zichtbaar
    return render(
        request,
        "properties/marketlisting_detail.html",
        {"listing": listing, "show_full": True, "paywall": False},
    )

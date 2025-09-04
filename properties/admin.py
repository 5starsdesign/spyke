from django.contrib import admin
from .models import (
    MarketListing, MarketListingImage,
    ExchangeOffer, ExchangeOfferImage, Wish
)

def has_field(model, name: str) -> bool:
    try:
        model._meta.get_field(name)
        return True
    except Exception:
        return False

# ---- MarketListing ----
class MarketListingAdmin(admin.ModelAdmin):
    list_display = [f for f in (
        'title', 'city', 'listing_kind', 'price',
        'is_published' if has_field(MarketListing, 'is_published') else None,
        'is_featured'  if has_field(MarketListing, 'is_featured')  else None,
        'created_at'   if has_field(MarketListing, 'created_at')   else None,
    ) if isinstance(f, str)]
    list_filter = [f for f in (
        'listing_kind', 'property_type', 'city',
        'is_published' if has_field(MarketListing, 'is_published') else None,
        'is_featured'  if has_field(MarketListing, 'is_featured')  else None,
    ) if isinstance(f, str)]
    search_fields = ('title', 'address', 'city', 'postcode')

admin.site.register(MarketListing, MarketListingAdmin)
admin.site.register(MarketListingImage)

# ---- ExchangeOffer (ruil) ----
class ExchangeOfferAdmin(admin.ModelAdmin):
    list_display = [f for f in (
        'member', 'my_title', 'my_city',
        'is_published' if has_field(ExchangeOffer, 'is_published') else None,
        'created_at'   if has_field(ExchangeOffer, 'created_at')   else None,
    ) if isinstance(f, str)]
    list_filter = [f for f in (
        'my_city',
        'is_published' if has_field(ExchangeOffer, 'is_published') else None,
    ) if isinstance(f, str)]
    search_fields = ('my_title', 'my_city', 'member__username', 'member__email')

admin.site.register(ExchangeOffer, ExchangeOfferAdmin)
admin.site.register(ExchangeOfferImage)
admin.site.register(Wish)

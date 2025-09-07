from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import ExchangeOffer, MarketListing


@admin.register(MarketListing)
class MarketListingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "city",
        "owner",
        "listing_kind",
        "published_marker",
        "view_link",
    )
    search_fields = ("title", "city", "address", "owner__username", "owner__email")
    list_filter = ("listing_kind", "is_published", "is_featured")

    def published_marker(self, obj):
        return format_html(
            '<span style="color:{};">{}</span>',
            "green" if obj.is_published else "red",
            "✅ Ja" if obj.is_published else "❌ Nee",
        )

    published_marker.short_description = "Gepubliceerd"

    def view_link(self, obj):
        url = (
            f"/woningen/{'huur' if obj.listing_kind == 'HUUR' else 'koop'}/{obj.slug}/"
        )
        return format_html('<a href="{}" target="_blank">Bekijk</a>', url)

    view_link.short_description = "Bekijk"


@admin.register(ExchangeOffer)
class ExchangeOfferAdmin(admin.ModelAdmin):
    list_display = ("my_title", "member", "my_city", "published_marker", "view_link")
    search_fields = ("my_title", "my_city", "member__username", "member__email")
    list_filter = ("is_published", "my_property_type", "my_city")

    def published_marker(self, obj):
        return format_html(
            '<span style="color:{};">{}</span>',
            "green" if obj.is_published else "red",
            "✅ Ja" if obj.is_published else "❌ Nee",
        )

    published_marker.short_description = "Gepubliceerd"

    def view_link(self, obj):
        url = f"/woningen/ruil/{obj.id}/"
        return format_html('<a href="{}" target="_blank">Bekijk</a>', url)

    view_link.short_description = "Bekijk"

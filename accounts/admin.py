from django.contrib import admin
from .models import AgencyProfile

@admin.register(AgencyProfile)
class AgencyProfileAdmin(admin.ModelAdmin):
    list_display = ("user","company_trade_name","company_legal_name","kvk_number","published","updated_at")
    list_filter = ("published",)
    search_fields = ("company_trade_name","company_legal_name","kvk_number","vat_number","user__username","user__email")

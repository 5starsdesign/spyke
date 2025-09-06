from django.contrib import admin
from django.contrib.auth import login, get_user_model
from django.shortcuts import redirect, get_object_or_404
from django.urls import path
from django.utils.html import format_html

from .models import Profile, AgencyProfile, OwnerProfile

User = get_user_model()


def login_as_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    login(request, user)
    return redirect("/mijn-dashboard/")


class UserAdminWithLogin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "go_to_dashboard")

    def role(self, obj):
        return getattr(getattr(obj, "profile", None), "role", "-")

    def go_to_dashboard(self, obj):
        return format_html(
            '<a class="button" href="/admin/login-as/{}/">Ga naar dashboard</a>',
            obj.pk,
        )
    go_to_dashboard.short_description = "Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("login-as/<int:user_id>/", self.admin_site.admin_view(login_as_view))
        ]
        return custom + urls


# Oude UserAdmin vervangen
admin.site.unregister(User)
admin.site.register(User, UserAdminWithLogin)

# Bestaande admin-registraties
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "premium")


@admin.register(AgencyProfile)
class AgencyProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_trade_name", "company_legal_name", "kvk_number", "published", "updated_at")
    list_filter = ("published",)
    search_fields = ("company_trade_name", "company_legal_name", "kvk_number", "vat_number", "user__username", "user__email")


@admin.register(OwnerProfile)
class OwnerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")

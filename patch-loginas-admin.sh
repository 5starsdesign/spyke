#!/bin/bash
set -e

# Backup (veiligheid eerst)
wr backup --name admin-loginas-patch || true
mkdir -p ~/bakkie-op
cp -a accounts/admin.py ~/bakkie-op/admin.py.$(date +%Y%m%d_%H%M%S).bak || true

# Schrijf een volledige, consistente admin.py
cat > accounts/admin.py <<'PY'
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import login
from django.shortcuts import redirect, get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html

from .models import Profile, AgencyProfile, OwnerProfile

User = get_user_model()

def login_as_view(request, user_id):
    # Alleen superusers
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    user = get_object_or_404(User, pk=user_id)
    login(request, user)
    return redirect("/mijn-dashboard/")

class UserProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fk_name = "user"

class UserAdminWithLogin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ("username", "email", "get_role", "is_staff", "is_superuser", "go_to_dashboard")

    def get_role(self, obj):
        return getattr(getattr(obj, "profile", None), "role", "-")
    get_role.short_description = "Rol"

    def go_to_dashboard(self, obj):
        # Correcte admin-URL onder /admin/auth/user/login-as/<id>/
        url = reverse(f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_login_as", args=[obj.pk])
        return format_html('<a class="button" href="{}">Ga naar dashboard</a>', url)
    go_to_dashboard.short_description = "Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        # Registreer een named URL in de admin-namespace
        custom = [
            path(
                "login-as/<int:user_id>/",
                self.admin_site.admin_view(login_as_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_login_as",
            )
        ]
        return custom + urls

# Vervang standaard UserAdmin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, UserAdminWithLogin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "premium", "city", "province")
    list_filter = ("role", "premium")
    search_fields = ("user__username", "user__email", "city", "province")

@admin.register(AgencyProfile)
class AgencyProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_trade_name", "company_legal_name", "kvk_number", "published", "updated_at")
    list_filter = ("published",)
    search_fields = ("company_trade_name", "company_legal_name", "kvk_number", "vat_number", "user__username", "user__email")

@admin.register(OwnerProfile)
class OwnerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")
PY

# Herstart + statics
docker compose exec -T web python manage.py collectstatic --noinput || true
docker compose restart web

echo "✅ Klaar. Ga in admin naar Gebruikers: kolom 'Dashboard' staat erbij."
echo "   De login-as URL is nu: /admin/auth/user/login-as/<user_id>/"

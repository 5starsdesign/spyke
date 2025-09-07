from django.conf import settings
from django.contrib import admin
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.urls import path

_original_get_urls = None  # origineel opslaan


def login_as_view(request, user_id):
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden

        return HttpResponseForbidden("Alleen superusers mogen dit")
    user = get_object_or_404(User, pk=user_id)
    user.backend = settings.AUTHENTICATION_BACKENDS[0]
    login(request, user)
    return redirect("/mijn-dashboard/")


def get_urls():
    global _original_get_urls
    urls = _original_get_urls()  # gebruik het origineel
    extra = [
        path(
            "login-as/<int:user_id>/",
            admin.site.admin_view(login_as_view),
            name="login_as",
        ),
    ]
    return extra + urls


def patch_user_admin():
    global _original_get_urls
    if _original_get_urls is None:
        _original_get_urls = admin.site.get_urls
        admin.site.get_urls = get_urls

#!/usr/bin/env bash
set -euo pipefail
cd "${HOME}/woningruil"

APP="newsletter"
mkdir -p $APP/management/commands

# 1) Model + admin
cat > $APP/models.py <<'PY'
from django.db import models

class Signup(models.Model):
    email = models.EmailField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} @ {self.created_at:%Y-%m-%d %H:%M}"
PY

cat > $APP/admin.py <<'PY'
from django.contrib import admin
from .models import Signup

@admin.register(Signup)
class SignupAdmin(admin.ModelAdmin):
    list_display = ("email","created_at","ip")
    search_fields = ("email","user_agent")
    list_filter = ("created_at",)
PY

# 2) View aanpassen: altijd lokaal loggen; Mailchimp alleen bij config
cat > $APP/views.py <<'PY'
import re
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_POST
from .models import Signup

@require_POST
def subscribe(request):
    email = (request.POST.get("email") or "").strip()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return HttpResponseBadRequest("Ongeldig e-mailadres")

    # Altijd lokaal bewaren
    Signup.objects.create(
        email=email,
        ip=(request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get("REMOTE_ADDR") or "").split(",")[0].strip(),
        user_agent=request.META.get("HTTP_USER_AGENT","")
    )

    api_key = getattr(settings, "MAILCHIMP_API_KEY", "")
    server  = getattr(settings, "MAILCHIMP_SERVER_PREFIX", "")
    list_id = getattr(settings, "MAILCHIMP_LIST_ID", "")
    double  = bool(getattr(settings, "MAILCHIMP_DOUBLE_OPTIN", True))

    if not (api_key and server and list_id):
        messages.success(request, "Inschrijving ontvangen. (Lokaal opgeslagen — Mailchimp nog niet geconfigureerd.)")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/?signup=1"))

    try:
        import mailchimp_marketing as MailchimpMarketing
        client = MailchimpMarketing.Client()
        client.set_config({"api_key": api_key, "server": server})
        payload = {"email_address": email, "status": "pending" if double else "subscribed"}
        client.lists.add_list_member(list_id, payload)
        messages.success(request, "Check je inbox om je inschrijving te bevestigen." if double else "Ingeschreven! Bedankt.")
    except Exception:
        messages.warning(request, "Lokaal opgeslagen; Mailchimp niet bereikbaar.")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/?signup=1"))
PY

# 3) Export-commando (CSV)
mkdir -p $APP/management/commands
cat > $APP/management/commands/export_newsletter_csv.py <<'PY'
from django.core.management.base import BaseCommand
from newsletter.models import Signup
import csv, sys

class Command(BaseCommand):
    help = "Exporteer newsletter signups naar CSV (stdout of pad)."

    def add_arguments(self, parser):
        parser.add_argument("--out", help="Pad naar CSV-bestand (default: stdout)")

    def handle(self, *args, **opts):
        qs = Signup.objects.all().order_by("-created_at")
        fields = ["created_at", "email", "ip", "user_agent"]
        if opts.get("out"):
            f = open(opts["out"], "w", newline="", encoding="utf-8")
        else:
            f = sys.stdout
        w = csv.writer(f)
        w.writerow(fields)
        for s in qs:
            w.writerow([s.created_at.isoformat(), s.email, s.ip or "", s.user_agent or ""])
        if opts.get("out"):
            f.close()
            self.stdout.write(self.style.SUCCESS(f"CSV geschreven: {opts['out']}"))
PY

# 4) CRLF→LF
sed -i 's/\r$//' $APP/models.py $APP/admin.py $APP/views.py $APP/management/commands/export_newsletter_csv.py

# 5) Migrations + build
docker compose up -d --build
docker compose exec -T web python manage.py makemigrations newsletter
docker compose exec -T web python manage.py migrate
docker compose exec -T web python manage.py collectstatic --noinput || true

echo "Nieuwsbrief lokaal opslaan actief. Test via footer-form; export met: python manage.py export_newsletter_csv --out /app/media/newsletter.csv"

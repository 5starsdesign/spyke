import re
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_POST
from .models import Signup

@require_POST
def subscribe(request):
    print("NEWSLETTER_SUBSCRIBE_VIEW_HIT")
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

from django import template
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

register = template.Library()

@register.simple_tag
def has_socialapp(provider):
    """Gebruik: {% has_socialapp 'google' as ok %}{% if ok %}...{% endif %}"""
    site = Site.objects.get_current()
    return SocialApp.objects.filter(provider=provider, sites=site).exists()

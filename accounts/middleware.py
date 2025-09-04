from django.http import HttpResponseRedirect
from django.urls import resolve

ALLOW_PREFIX = ("/static/", "/media/", "/accounts/", "/health/", "/favicon", "/robots.txt")
ALLOW_EXACT  = ("/",)

class AnonHomeOnlyMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        u = getattr(request, "user", None)
        if u and u.is_authenticated:
            return self.get_response(request)

        path = request.path
        if path in ALLOW_EXACT or path.startswith(ALLOW_PREFIX):
            return self.get_response(request)

        # Laat admin-login scherm toe:
        if path.startswith("/admin/"):
            try:
                match = resolve(path)
                if match and match.app_name == "admin":
                    return self.get_response(request)
            except Exception:
                pass

        # Alles anders: terug naar home met signup-popup
        return HttpResponseRedirect("/?signup=1")

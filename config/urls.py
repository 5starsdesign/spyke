from accounts import admin_login_as_patch
from pages import agency_public
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from dashboards.views import my_dashboard_redirect


def health(_): return HttpResponse("ok")

urlpatterns = [
    path('nieuwsbrief/', include(('newsletter.urls','newsletter'), namespace='newsletter')),
    path('blog/', include(('blog.urls','blog'), namespace='blog')),
    path("makelaars/<slug:slug>/", agency_public.agency_public_profile, name="agency_public_profile"),
    path("admin/", admin.site.urls),
    path("health/", health),

    # Publiek
    path("", include("pages.urls"), name="home"),
    path("ruilwoningen/", include("properties.urls"), name="ruil_list_public"),  # pages/props regelen intern
    path("huurwoningen/", include("properties.urls"), name="huur_list_public"),
    path("koopwoningen/", include("properties.urls"), name="koop_list_public"),
    path("makelaar/", include("pages.urls")),   # publieke makelaars-pagina's
    path("woningen/", include("properties.urls")),
    path("accounts/", include("allauth.urls")),

    # Dashboards
    path("dash/", include("dashboards.urls")),
    path("mijn-dashboard/", my_dashboard_redirect, name="my_dashboard"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns.append(path("admin/login-as/<int:user_id>/", admin_login_as_patch.login_as_view, name="admin_login_as"))

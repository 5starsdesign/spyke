from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("ruilwoningen/", views.ruil_list, name="ruil_list_public"),
    path("huurwoningen/", views.huur_list, name="huur_list_public"),
    path("koopwoningen/", views.koop_list, name="koop_list_public"),
    path("makelaar/<slug:slug>/", views.agency_public, name="agency_public"),
]

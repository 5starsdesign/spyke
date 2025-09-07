from django.urls import path

from . import views

urlpatterns = [
    path(
        "huur/<slug:slug>/", views.market_detail, {"kind": "HUUR"}, name="huur_detail"
    ),
    path(
        "koop/<slug:slug>/", views.market_detail, {"kind": "KOOP"}, name="koop_detail"
    ),
    path("ruil/<int:pk>/", views.exchange_detail, name="ruil_detail"),
]

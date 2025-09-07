from django.urls import path

from . import views

app_name = "blog"
urlpatterns = [
    path("", views.list_view, name="list"),
    path("categorie/<slug:category_slug>/", views.list_view, name="by_category"),
    path("tag/<slug:tag_slug>/", views.list_view, name="by_tag"),
    path("archief/<int:year>/<int:month>/", views.list_view, name="archive"),
    path("<slug:slug>/", views.detail_view, name="detail"),
]

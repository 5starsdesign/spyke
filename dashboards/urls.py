from django.urls import path
from django.views.generic import RedirectView
from . import member_views, agency_views, owner_views

urlpatterns = [
    # --- MEMBER ---
    path("member/", member_views.member_home, name="member_home"),
    path("member/profiel/", member_views.member_profile, name="member_profile"),

    # Eigen woning
    path("member/eigen/bewerken/", member_views.member_own, name="member_own"),
    path("member/eigen/overzicht/", member_views.member_own_view, name="member_own_view"),
    path("member/eigen/", RedirectView.as_view(pattern_name="member_own_view", permanent=False)),

    # Wens
    path("member/wens/", member_views.member_wish, name="member_wish"),
    path("member/wens/overzicht/", member_views.member_wish_view, name="member_wish_view"),

    # Matches
    path("member/matches/", member_views.member_matches, name="member_matches"),

    # Alias voor woning → altijd overzicht
    path("member/woning/", RedirectView.as_view(pattern_name="member_own_view", permanent=False)),

    # --- OWNER ---
    path("owner/", owner_views.owner_home, name="owner_home"),
    path("owner/mijn/", owner_views.owner_my, name="owner_my"),
    path("owner/nieuw/", owner_views.owner_new, name="owner_new"),
    path("owner/<slug:slug>/bewerken/", owner_views.owner_listing_edit, name="owner_listing_edit"),
    path("owner/profiel/", owner_views.owner_profile, name="owner_profile"),
    path("owner/woning/", RedirectView.as_view(pattern_name="owner_my", permanent=False)),

    # --- AGENCY ---
    path("agency/", agency_views.agency_home, name="agency_home"),
    path("agency/mijn/", agency_views.agency_home, name="agency_home_mijn"),
    path("agency/nieuw/", agency_views.agency_new, name="agency_new"),
    path("agency/<slug:slug>/bewerken/", agency_views.agency_listing_edit, name="agency_listing_edit"),
    path("agency/profiel/", agency_views.agency_profile, name="agency_profile"),
    path("agency/woning/", RedirectView.as_view(pattern_name="agency_home_mijn", permanent=False)),
]

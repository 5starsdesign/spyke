from . import owner_views
from . import agency_views
from django.urls import path
from . import member_views, agency_views, owner_views

urlpatterns = [
    path("member/profiel/", member_views.member_profile, name="member_profile"),
    path("member/wens/overzicht/", member_views.member_wish_view, name="member_wish_view"),
    path("member/wens/", member_views.member_wish, name="member_wish"),
    # --- MEMBER ---
    path("member/",                    member_views.member_home,        name="member_home"),
    path("member/profiel/",            member_views.member_profile,     name="member_profile"),
    path("member/eigen/",              member_views.member_own,         name="member_own"),
    path("member/wens/",               member_views.member_wish,        name="member_wish"),
    path("member/matches/",            member_views.member_matches,     name="member_matches"),

    # --- AGENCY ---
    path("agency/",                    agency_views.agency_home,        name="agency_home"),
    path("agency/mijn/",               agency_views.agency_home,          name="agency_home"),
    path("agency/nieuw/",              agency_views.agency_new,         name="agency_new"),
    path("agency/<slug:slug>/bewerken/", agency_views.agency_listing_edit, name="agency_listing_edit"),
    path("agency/profiel/",            agency_views.agency_profile,     name="agency_profile"),

    # --- OWNER ---
    path("owner/",                     owner_views.owner_home,          name="owner_home"),
    path("owner/mijn/",                owner_views.owner_my,            name="owner_my"),
    path("owner/nieuw/",               owner_views.owner_new,           name="owner_new"),
    path("owner/<slug:slug>/bewerken/", owner_views.owner_listing_edit, name="owner_listing_edit"),
    path("owner/profiel/",             owner_views.owner_profile,       name="owner_profile"),
]

urlpatterns += [path("member/eigen/overzicht/", member_views.member_own_view, name="member_own_view"),]

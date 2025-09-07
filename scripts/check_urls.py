from django.urls import reverse, NoReverseMatch, get_resolver

def check(path, name=None, kwargs=None):
    try:
        if name:
            reverse(name, kwargs=kwargs or {})
        print(f"Check {path} ... ✅ OK")
    except NoReverseMatch:
        print(f"Check {path} ... ❌ MISSING")

print("=== URL CHECK ===")
check("/", "home")
check("/ruilwoningen/", "ruil_list_public")
check("/huurwoningen/", "huur_list_public")
check("/koopwoningen/", "koop_list_public")

check("/woningen/huur/<slug:slug>/", "huur_detail", {"slug": "test-slug"})
check("/woningen/koop/<slug:slug>/", "koop_detail", {"slug": "test-slug"})
check("/woningen/ruil/<int:pk>/", "ruil_detail", {"pk": 1})

check("/accounts/", "account_login")  # voorbeeld
check("/dash/member/", "member_home")
check("/dash/agency/mijn/", "agency_home_mijn")
check("/dash/agency/<slug:slug>/bewerken/", "agency_listing_edit", {"slug": "test-slug"})

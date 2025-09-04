def access_flags(request):
    user = getattr(request, "user", None)
    is_auth = bool(getattr(user, "is_authenticated", False))
    is_premium = False
    try:
        prof = getattr(user, "profile", None)
        is_premium = bool(getattr(prof, "is_premium", False))
    except Exception:
        is_premium = False
    return {
        "ACCESS": {
            "is_auth": is_auth,
            "is_premium": is_premium,
            "can_view_full": is_premium,
            "can_view_blur": is_auth and not is_premium,
            "must_signup": not is_auth,
        }
    }

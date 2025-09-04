from properties.models import MarketListing, MarketListingImage

def _get_listing_model():
    return MarketListing

def _get_listing_image_model():
    return MarketListingImage

def _has_field(model_or_instance, field_name: str) -> bool:
    model = getattr(getattr(model_or_instance, "_meta", None), "model", None) or model_or_instance
    try:
        model._meta.get_field(field_name)
        return True
    except Exception:
        return False

def _owned_qs(user, model=None):
    model = model or MarketListing
    try:
        if _has_field(model, "owner"):
            return model._default_manager.filter(owner=user)
        return model._default_manager.none()
    except Exception:
        return model._default_manager.none()

def _slug_or_pk(value, slug_field: str = "slug"):
    v = ("" if value is None else str(value)).strip()
    try:
        return {"pk": int(v)}
    except (TypeError, ValueError):
        return {slug_field: v}

def _get_by_slug_or_pk(model, value, slug_field: str = "slug"):
    return model._default_manager.get(**_slug_or_pk(value, slug_field=slug_field))

def _kind_path(kind_or_obj) -> str:
    k = None
    if isinstance(kind_or_obj, str):
        k = kind_or_obj.strip().upper()
    elif hasattr(kind_or_obj, "listing_kind"):
        k = str(kind_or_obj.listing_kind).upper()
    else:
        k = "HUUR"
    if k in ("KOOP", getattr(MarketListing, "K_KOOP", "KOOP")):
        return "koop"
    return "huur"

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from accounts.models import Profile
from dashboards.owner_forms import OwnerListingForm, OwnerProfileForm
from properties.models import MarketListing, MarketListingImage

from .owner_new_form import OwnerNewForm


@login_required
def owner_home(request):
    return redirect("owner_my")


@login_required
def owner_my(request):
    listings = MarketListing.objects.filter(owner=request.user).order_by("-updated_at")
    return render(request, "dash/owner/my.html", {"listings": listings})


@login_required
def owner_new(request):
    if request.method == "POST":
        form = OwnerNewForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            from properties.models import MarketListing, MarketListingImage

            with transaction.atomic():
                obj = MarketListing(
                    owner=request.user,
                    title=cd["title"],
                    listing_kind=cd["listing_kind"],
                    address=form.to_address(),
                    postcode=cd["postcode"],
                    city=cd["city"],
                    province=cd["province"],
                    property_type=cd["property_type"],
                    build_year=cd.get("build_year") or None,
                    living_area=cd["living_area"],
                    lot_area=cd.get("lot_area") or None,
                    rooms=cd["rooms"],
                    bedrooms=cd.get("bedrooms") or 0,
                    bathrooms=cd.get("bathrooms") or 0,
                    floors=cd.get("floors") or 0,
                    energy_label=cd.get("energy_label") or "",
                    price=cd["price"],
                    available_from=cd.get("available_from") or None,
                    service_costs=cd.get("service_costs") or None,
                    deposit=cd.get("deposit") or None,
                    solar_panels=cd.get("solar_panels") or False,
                    heat_pump=cd.get("heat_pump") or False,
                    storage=cd.get("storage") or False,
                    shed=cd.get("shed") or False,
                    parking_garage=cd.get("parking_garage") or False,
                    parking_spot=cd.get("parking_spot") or False,
                    garden=cd.get("garden") or False,
                    balcony=cd.get("balcony") or False,
                    terrace=cd.get("terrace") or False,
                    elevator=cd.get("elevator") or False,
                    wheelchair_accessible=cd.get("wheelchair_accessible") or False,
                    new_build=bool(cd.get("extension")),
                    smoking_allowed=cd.get("smoking_allowed") or False,
                    pets_allowed=cd.get("pets_allowed") or False,
                    suitable_for=cd.get("suitable_for") or "",
                )
                # slug fallback
                if not getattr(obj, "slug", None):
                    pass
                if not obj.slug:
                    obj.slug = _unique_slug(MarketListing, f"{obj.title}-{obj.city}")
                obj.description = obj.description or ""
                obj.save()

                # Media
                if request.FILES.get("cover"):
                    MarketListingImage.objects.create(
                        listing=obj, image=request.FILES["cover"]
                    )
                for f in request.FILES.getlist("gallery"):
                    MarketListingImage.objects.create(listing=obj, image=f)
                if request.FILES.get("floorplan"):
                    MarketListingImage.objects.create(
                        listing=obj, image=request.FILES["floorplan"]
                    )

            messages.success(request, "Woning aangemaakt.")
            return redirect("owner_my")
        else:
            # toon eerste fouten in bericht
            first = (
                next(iter(form.errors.values()))[0]
                if form.errors
                else "Onbekende validatiefout."
            )
            messages.error(request, f"Kan niet opslaan: {first}")
    else:
        form = OwnerNewForm()
    return render(request, "dash/owner/new.html", {"form": form})


@login_required
def owner_listing_edit(request, slug):
    obj = get_object_or_404(MarketListing, slug=slug, owner=request.user)
    if request.method == "POST":
        form = OwnerListingForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            obj = form.save()
            # uploads
            if request.FILES.get("new_cover"):
                MarketListingImage.objects.create(
                    listing=obj, image=request.FILES["new_cover"]
                )
            for f in request.FILES.getlist("new_gallery"):
                MarketListingImage.objects.create(listing=obj, image=f)
            messages.success(request, "Woning opgeslagen.")
            return redirect("owner_my")
    else:
        form = OwnerListingForm(instance=obj)
    return render(request, "dash/owner/edit.html", {"form": form, "obj": obj})


@login_required
def owner_profile(request):
    obj, _ = Profile.objects.get_or_create(user=request.user)
    editing = request.method == "POST" or request.GET.get("edit") == "1"
    if request.method == "POST":
        form = OwnerProfileForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Profiel opgeslagen.")
            return redirect("owner_profile")
    else:
        form = OwnerProfileForm(instance=obj)
    return render(
        request,
        "dash/owner/profile.html",
        {"form": form, "obj": obj, "editing": editing},
    )


def _unique_slug(model, base):
    base = (slugify(base) or "listing")[:200]
    cand = base
    i = 2
    while model.objects.filter(slug=cand).exists():
        cand = f"{base}-{i}"[:220]
        i += 1
    return cand

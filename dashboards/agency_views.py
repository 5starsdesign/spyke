from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from dashboards.agency_forms import AgencyListingForm
from dashboards.agency_new_form import AgencyNewForm
from properties.models import MarketListing, MarketListingImage

from .agency_forms import AgencyListingForm
from .utils import (_get_by_slug_or_pk, _get_listing_image_model,
                    _get_listing_model, _has_field, _kind_path, _owned_qs,
                    _slug_or_pk)


@login_required
def agency_home(request):
    q = (request.GET.get("q") or "").strip()
    qs = _owned_qs(request.user, MarketListing).order_by("-created_at")
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(address__icontains=q)
            | Q(city__icontains=q)
            | Q(postcode__icontains=q)
        )
    return render(request, "dash/agency/home.html", {"listings": qs, "q": q})


# Backwards-compat alias
def agency_my(request):
    return agency_home(request)


@login_required
def agency_new(request):
    if request.method == "POST":
        form = AgencyListingForm(request.POST, request.FILES)
        if form.is_valid():
            inst = form.save(owner=request.user)
            messages.success(request, "Woning opgeslagen.")
            return redirect("agency_listing_edit", slug=inst.slug)
    else:
        form = AgencyListingForm()
    return render(request, "dash/agency/new.html", {"form": form})


@login_required
def agency_listing_edit(request, slug):
    obj = MarketListing.objects.filter(slug=slug, owner=request.user).first()
    if not obj:
        from django.http import Http404

        raise Http404("Listing niet gevonden")
    if request.method == "POST":
        form = AgencyListingForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            obj = form.save()
            # uploads verwerken
            if request.FILES.get("new_cover"):
                MarketListingImage.objects.create(
                    listing=obj, image=request.FILES["new_cover"]
                )
            for f in request.FILES.getlist("new_gallery"):
                MarketListingImage.objects.create(listing=obj, image=f)
            messages.success(request, "Woning opgeslagen.")
            return redirect("agency_listing_edit", slug=obj.slug)
    else:
        form = AgencyListingForm(instance=obj)
    return render(request, "dash/agency/edit.html", {"form": form, "obj": obj})


@login_required
def agency_profile(request):
    """
    Simpele profielpagina voor makelaar/eigenaar.
    Losstaand van members.
    """
    return render(request, "dash/agency/profile.html", {"user_obj": request.user})


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.models import AgencyProfile
from dashboards.agency_profile_forms import AgencyProfileForm


@login_required
def agency_profile(request):
    obj, _ = AgencyProfile.objects.get_or_create(user=request.user)
    editing = request.method == "POST" or request.GET.get("edit") == "1"
    if request.method == "POST":
        form = AgencyProfileForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.user = request.user
            inst.save()
            messages.success(request, "Profiel opgeslagen.")
            return redirect("agency_profile")
    else:
        form = AgencyProfileForm(instance=obj)
    return render(
        request,
        "dash/agency/profile.html",
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


@login_required
def agency_new(request):
    if request.method == "POST":
        form = AgencyNewForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
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
                    garden=cd.get("garden") or False,
                    balcony=cd.get("balcony") or False,
                    terrace=cd.get("terrace") or False,
                    roof_terrace=cd.get("roof_terrace") or False,
                    storage=cd.get("storage") or False,
                    shed=cd.get("shed") or False,
                    parking_garage=cd.get("parking_garage") or False,
                    parking_spot=cd.get("parking_spot") or False,
                    elevator=cd.get("elevator") or False,
                    wheelchair_accessible=cd.get("wheelchair_accessible") or False,
                    new_build=cd.get("new_build") or False,
                    solar_panels=cd.get("solar_panels") or False,
                    heat_pump=cd.get("heat_pump") or False,
                    smoking_allowed=cd.get("smoking_allowed") or False,
                    pets_allowed=cd.get("pets_allowed") or False,
                    suitable_for=cd.get("suitable_for") or "",
                    description=cd.get("description") or "",
                )
                if not getattr(obj, "slug", None):
                    pass
                if not obj.slug:
                    obj.slug = _unique_slug(MarketListing, f"{obj.title}-{obj.city}")
                obj.save()

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
            return redirect("/dash/agency/")
    else:
        form = AgencyNewForm()
    return render(request, "dash/agency/new.html", {"form": form})

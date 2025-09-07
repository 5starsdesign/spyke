from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from accounts.models import Profile
from matchmaking.utils import find_matches_for
from properties.forms import ExchangeOfferForm, MarketListingForm
from properties.models import ExchangeOffer, MarketListing


def role_guard(user, role):
    if not user.is_authenticated:
        return False
    try:
        return user.profile.role == role
    except Profile.DoesNotExist:
        return False


def role_required(role):
    def dec(fn):
        def wrapper(request, *a, **kw):
            if not role_guard(request.user, role):
                return HttpResponseForbidden("Geen toegang")
            return fn(request, *a, **kw)

        return login_required(wrapper)

    return dec


# --- MEMBER ---
@role_required(Profile.ROLE_MEMBER)
def member_home(request):
    offer = ExchangeOffer.objects.filter(member=request.user).first()
    matches = find_matches_for(offer) if offer else []
    return render(
        request, "dash/member/home.html", {"offer": offer, "matches": matches}
    )


@role_required(Profile.ROLE_MEMBER)
def member_profile(request):
    prof = request.user.profile
    if request.method == "POST":
        prof.display_name = request.POST.get("display_name", "")
        prof.city = request.POST.get("city", "")
        prof.bio = request.POST.get("bio", "")
        prof.save()
        return redirect("dash_member")
    return render(request, "dash/member/profile.html", {"profile": prof})


@role_required(Profile.ROLE_MEMBER)
def member_edit_offer(request):
    offer = ExchangeOffer.objects.filter(member=request.user).first()
    if request.method == "POST":
        form = ExchangeOfferForm(request.POST, request.FILES, instance=offer)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.member = request.user
            obj.save()
            return redirect("dash_member")
    else:
        form = ExchangeOfferForm(instance=offer)
    return render(request, "dash/member/offer_form.html", {"form": form})


@role_required(Profile.ROLE_MEMBER)
def member_matches(request):
    offer = ExchangeOffer.objects.filter(member=request.user).first()
    matches = find_matches_for(offer) if offer else []
    return render(request, "dash/member/matches.html", {"matches": matches})


# --- OWNER ---
@role_required(Profile.ROLE_OWNER)
def owner_home(request):
    items = MarketListing.objects.filter(owner=request.user)
    return render(request, "dash/owner/home.html", {"items": items})


@role_required(Profile.ROLE_OWNER)
def owner_profile(request):
    prof = request.user.profile
    if request.method == "POST":
        prof.display_name = request.POST.get("display_name", "")
        prof.city = request.POST.get("city", "")
        prof.save()
        return redirect("dash_owner")
    return render(request, "dash/owner/profile.html", {"profile": prof})


@role_required(Profile.ROLE_OWNER)
def owner_new_listing(request):
    if request.method == "POST":
        form = MarketListingForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.is_published = True
            obj.save()
            return redirect("dash_owner_list")
    else:
        form = MarketListingForm()
    return render(request, "dash/owner/listing_form.html", {"form": form})


@role_required(Profile.ROLE_OWNER)
def owner_my_listings(request):
    items = MarketListing.objects.filter(owner=request.user)
    return render(request, "dash/owner/list.html", {"items": items})


# --- AGENCY ---
@role_required(Profile.ROLE_AGENCY)
def agency_home(request):
    items = MarketListing.objects.filter(owner=request.user)
    return render(request, "dash/agency/home.html", {"items": items})


@role_required(Profile.ROLE_AGENCY)
def agency_profile(request):
    prof = request.user.profile
    if request.method == "POST":
        prof.company_name = request.POST.get("company_name", "")
        prof.address = request.POST.get("address", "")
        prof.city = request.POST.get("city", "")
        prof.phone = request.POST.get("phone", "")
        prof.save()
        return redirect("dash_agency")
    return render(request, "dash/agency/profile.html", {"profile": prof})


@role_required(Profile.ROLE_AGENCY)
def agency_new_listing(request):
    if request.method == "POST":
        form = MarketListingForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.is_published = True
            obj.save()
            return redirect("dash_agency_list")
    else:
        form = MarketListingForm()
    return render(request, "dash/agency/listing_form.html", {"form": form})


@role_required(Profile.ROLE_AGENCY)
def agency_my_listings(request):
    items = MarketListing.objects.filter(owner=request.user)
    return render(request, "dash/agency/list.html", {"items": items})


# --- Redirect ---
@login_required
def my_dashboard_redirect(request):
    role = getattr(request.user.profile, "role", None)
    if role == Profile.ROLE_MEMBER:
        return redirect("member_home")
    elif role == Profile.ROLE_OWNER:
        return redirect("owner_home")
    elif role == Profile.ROLE_AGENCY:
        return redirect("agency_home")
    return redirect("/")

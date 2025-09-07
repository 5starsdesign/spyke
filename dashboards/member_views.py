from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from accounts.models import Profile
from properties.models import ExchangeOffer, Wish

from .forms import ExchangeImageFormSet, MemberOwnForm, ProfileForm, WishForm


@login_required
def member_home(request):
    return render(request, "dash/member/home.html")


@login_required
def member_matches(request):
    return render(request, "dash/member/matches.html")


# --- Eigen woning (bewerken) ---
@login_required
def member_own(request):
    obj, _ = ExchangeOffer.objects.get_or_create(
        member=request.user, defaults={"is_published": False}
    )
    if request.method == "POST":
        form = MemberOwnForm(request.POST, request.FILES, instance=obj)
        formset = ExchangeImageFormSet(request.POST, request.FILES, instance=obj)
        publish = "publish" in request.POST

        if form.is_valid() and formset.is_valid():
            inst = form.save(commit=False)
            inst.member = request.user

            if publish:
                inst.is_published = True
                try:
                    inst.full_clean()
                except ValidationError as e:
                    for fld, msgs in e.message_dict.items():
                        for m in msgs:
                            form.add_error(fld, m)
                    messages.error(
                        request, "Publiceren mislukt: vul alle verplichte velden in."
                    )
                    inst.is_published = False
                else:
                    inst.save()
                    formset.instance = inst
                    formset.save()
                    messages.success(request, "Woning gepubliceerd.")
                    return redirect("member_own_view")

            # gewone opslaan → ook naar overzicht
            inst.save()
            formset.instance = inst
            formset.save()
            messages.success(request, "Gegevens opgeslagen.")
            return redirect("member_own_view")

    else:
        form = MemberOwnForm(instance=obj)
        formset = ExchangeImageFormSet(instance=obj)

    return render(request, "dash/member/own.html", {"form": form, "formset": formset})


# --- Eigen woning overzicht (readonly) ---
@login_required
def member_own_view(request):
    obj, _ = ExchangeOffer.objects.get_or_create(
        member=request.user, defaults={"is_published": False}
    )
    images = obj.images.all()
    return render(request, "dash/member/own_view.html", {"obj": obj, "images": images})


# --- Wens (bewerk) ---
@login_required
def member_wish(request):
    wish, _ = Wish.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = WishForm(request.POST, instance=wish)
        if form.is_valid():
            form.save()
            messages.success(request, "Zoekprofiel opgeslagen.")
            return redirect("member_wish_view")
    else:
        form = WishForm(instance=wish)
    return render(request, "dash/member/wish.html", {"form": form})


# --- Wens (readonly) ---
@login_required
def member_wish_view(request):
    wish, _ = Wish.objects.get_or_create(user=request.user)
    return render(request, "dash/member/wish_view.html", {"wish": wish})


# --- Profiel (readonly of edit via ?edit=1) ---
@login_required
def member_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    user = request.user

    edit_mode = request.GET.get("edit") in ("1", "true", "True")
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Update ook de user-data
            user.first_name = request.POST.get("first_name", user.first_name)
            user.last_name = request.POST.get("last_name", user.last_name)
            user.email = request.POST.get("email", user.email)
            user.save()

            messages.success(request, "Profiel opgeslagen.")
            return redirect("member_profile")
    else:
        form = ProfileForm(instance=profile)

    ctx = {
        "form": form,
        "profile": profile,
        "user": user,
        "edit_mode": edit_mode,
        "has_password": user.has_usable_password(),
    }
    return render(request, "dash/member/profile.html", ctx)

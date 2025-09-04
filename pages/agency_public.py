from django.shortcuts import render, get_object_or_404
from accounts.models import AgencyProfile
def agency_public_profile(request, slug):
    obj = get_object_or_404(AgencyProfile, slug=slug, published=True)
    return render(request, "agency/public_profile.html", {"obj": obj})

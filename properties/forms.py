from django import forms
from .models import MarketListing, ExchangeOffer
class MarketListingForm(forms.ModelForm):
    class Meta:
        model = MarketListing
        exclude = ("owner","slug","is_featured","is_published",)
        widgets = {"description": forms.Textarea(attrs={"rows":4})}
class ExchangeOfferForm(forms.ModelForm):
    class Meta:
        model = ExchangeOffer
        exclude = ("member","is_published",)
        widgets = {"my_description": forms.Textarea(attrs={"rows":4})}

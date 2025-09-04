from django.forms.widgets import ClearableFileInput
from django import forms
from properties.models import MarketListing

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

class MultiFileField(forms.FileField):
    def clean(self, data, initial=None):
        if not data:
            return []
        if isinstance(data, (list, tuple)):
            return [super().clean(f, initial) for f in data if f]
        return [super().clean(data, initial)]


class OwnerListingForm(forms.ModelForm):
    

    new_cover = forms.ImageField(required=False, label="Nieuwe coverfoto")
    new_gallery = MultiFileField(required=False, widget=MultiFileInput(attrs={"multiple": True}), label="Nieuwe galerij-foto's (meerdere)")

    # -- NL labels force --
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            "title":"Titel","address":"Adres","postcode":"Postcode","city":"Plaats","province":"Provincie",
            "listing_kind":"Aanbodtype","property_type":"Type woning","price":"Prijs (€)",
            "living_area":"Woonoppervlakte (m²)","rooms":"Aantal kamers","bedrooms":"Aantal slaapkamers",
            "bathrooms":"Aantal badkamers","floors":"Aantal verdiepingen","lot_area":"Perceeloppervlakte (m²)",
            "build_year":"Bouwjaar","energy_label":"Energielabel",
            "garden":"Tuin","balcony":"Balkon","terrace":"Terras","roof_terrace":"Dakterras",
            "storage":"Berging","shed":"Schuur","parking_garage":"Garage","parking_spot":"Eigen parkeerplaats",
            "elevator":"Lift","wheelchair_accessible":"Rolstoeltoegankelijk","new_build":"Nieuwbouw",
            "solar_panels":"Zonnepanelen","heat_pump":"Warmtepomp",
            "smoking_allowed":"Roken toegestaan","pets_allowed":"Huisdieren toegestaan",
            "suitable_for":"Geschikt voor","description":"Beschrijving",
        }
        for k,v in labels.items():
            if k in self.fields:
                self.fields[k].label = v

    class Meta:
        model = MarketListing
        fields = (
            "title","address","postcode","city","province",
            "listing_kind","property_type","price",
            "living_area","rooms","bedrooms","bathrooms","floors",
            "lot_area","build_year","energy_label",
            "garden","balcony","terrace","roof_terrace",
            "storage","shed","parking_garage","parking_spot",
            "elevator","wheelchair_accessible","new_build","solar_panels","heat_pump",
            "description",
        )
        widgets = {f: forms.TextInput(attrs={"class":"form-control"}) for f in
                   ("title","address","postcode","city","province","price","living_area","rooms","bedrooms","bathrooms","floors","lot_area","build_year","energy_label")}
        widgets.update({
            "listing_kind": forms.Select(attrs={"class":"form-select"}),
            "property_type": forms.Select(attrs={"class":"form-select"}),
            "description": forms.Textarea(attrs={"class":"form-control","rows":5}),
            "garden": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "balcony": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "terrace": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "roof_terrace": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "storage": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "shed": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "parking_garage": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "parking_spot": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "elevator": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "wheelchair_accessible": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "new_build": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "solar_panels": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "heat_pump": forms.CheckboxInput(attrs={"class":"form-check-input"}),
        })

from accounts.models import Profile
class OwnerProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar","address","postcode","city","province")
        widgets = {
            "address":  forms.TextInput(attrs={"class":"form-control"}),
            "postcode": forms.TextInput(attrs={"class":"form-control"}),
            "city":     forms.TextInput(attrs={"class":"form-control"}),
            "province": forms.TextInput(attrs={"class":"form-control"}),
            "avatar":   forms.ClearableFileInput(attrs={"class":"form-control"}),
        }

        labels = {
            "title":"Titel","address":"Adres","postcode":"Postcode","city":"Plaats","province":"Provincie",
            "listing_kind":"Aanbodtype","property_type":"Type woning","price":"Prijs (€)",
            "living_area":"Woonoppervlakte (m²)","rooms":"Aantal kamers","bedrooms":"Aantal slaapkamers",
            "bathrooms":"Aantal badkamers","floors":"Aantal verdiepingen","lot_area":"Perceeloppervlakte (m²)",
            "build_year":"Bouwjaar","energy_label":"Energielabel",
            "garden":"Tuin","balcony":"Balkon","terrace":"Terras","roof_terrace":"Dakterras",
            "storage":"Berging","shed":"Schuur","parking_garage":"Garage","parking_spot":"Eigen parkeerplaats",
            "elevator":"Lift","wheelchair_accessible":"Rolstoeltoegankelijk","new_build":"Nieuwbouw",
            "solar_panels":"Zonnepanelen","heat_pump":"Warmtepomp",
            "smoking_allowed":"Roken toegestaan","pets_allowed":"Huisdieren toegestaan",
            "suitable_for":"Geschikt voor","description":"Beschrijving"
        }


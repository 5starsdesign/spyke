from django import forms
from django.forms.widgets import ClearableFileInput

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


class AgencyListingForm(forms.ModelForm):
    # extra uploadvelden naast model
    new_cover = forms.ImageField(required=False, label="Nieuwe coverfoto")
    new_gallery = MultiFileField(
        required=False,
        widget=MultiFileInput(attrs={"multiple": True}),
        label="Nieuwe galerij-foto's (meerdere)",
    )

    class Meta:
        model = MarketListing
        fields = (
            "listing_kind",
            "title",
            "available_from",
            "address",
            "postcode",
            "city",
            "province",
            "property_type",
            "build_year",
            "living_area",
            "lot_area",
            "rooms",
            "bedrooms",
            "bathrooms",
            "floors",
            "energy_label",
            "garden",
            "balcony",
            "terrace",
            "roof_terrace",
            "storage",
            "shed",
            "parking_garage",
            "parking_spot",
            "elevator",
            "wheelchair_accessible",
            "new_build",
            "solar_panels",
            "heat_pump",
            "smoking_allowed",
            "pets_allowed",
            "suitable_for",
            "price",
            "service_costs",
            "deposit",
            "description",
        )
        labels = {  # NL labels
            "listing_kind": "Aanbodtype",
            "title": "Titel",
            "available_from": "Beschikbaar per",
            "address": "Adres",
            "postcode": "Postcode",
            "city": "Plaats",
            "province": "Provincie",
            "property_type": "Type woning",
            "build_year": "Bouwjaar",
            "living_area": "Woonoppervlakte (m²)",
            "lot_area": "Perceeloppervlakte (m²)",
            "rooms": "Aantal kamers",
            "bedrooms": "Aantal slaapkamers",
            "bathrooms": "Aantal badkamers",
            "floors": "Aantal verdiepingen",
            "energy_label": "Energielabel",
            "garden": "Tuin",
            "balcony": "Balkon",
            "terrace": "Terras",
            "roof_terrace": "Dakterras",
            "storage": "Berging",
            "shed": "Schuur",
            "parking_garage": "Garage",
            "parking_spot": "Eigen parkeerplaats",
            "elevator": "Lift",
            "wheelchair_accessible": "Rolstoeltoegankelijk",
            "new_build": "Nieuwbouw",
            "solar_panels": "Zonnepanelen",
            "heat_pump": "Warmtepomp",
            "smoking_allowed": "Roken toegestaan",
            "pets_allowed": "Huisdieren toegestaan",
            "suitable_for": "Geschikt voor",
            "price": "Prijs (€)",
            "service_costs": "Servicekosten p/m",
            "deposit": "Waarborgsom (€)",
            "description": "Beschrijving",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django import forms as _f
        from django.forms.widgets import (CheckboxInput, ClearableFileInput,
                                          DateInput, EmailInput, NumberInput,
                                          RadioSelect, Select, Textarea,
                                          TextInput, URLInput)

        # Forceer radio's voor Aanbodtype
        self.fields["listing_kind"].widget = RadioSelect(
            choices=(("HUUR", "Huur"), ("KOOP", "Koop"))
        )
        # Datumveld als <input type="date">
        if hasattr(self.fields.get("available_from", ""), "widget"):
            self.fields["available_from"].widget = DateInput(attrs={"type": "date"})
        # Prijs als nummer met decimals
        if hasattr(self.fields.get("price", ""), "widget"):
            self.fields["price"].widget = NumberInput(attrs={"step": "0.01"})

        # Bootstrap klassen
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(
                w, (TextInput, NumberInput, URLInput, EmailInput, DateInput, Textarea)
            ):
                w.attrs["class"] = (w.attrs.get("class", "") + " form-control").strip()
            elif isinstance(w, Select):
                w.attrs["class"] = (w.attrs.get("class", "") + " form-select").strip()
            elif isinstance(w, CheckboxInput):
                w.attrs["class"] = (
                    w.attrs.get("class", "") + " form-check-input"
                ).strip()
            elif isinstance(w, RadioSelect):
                w.attrs["class"] = (
                    w.attrs.get("class", "") + " form-check-input"
                ).strip()
            elif isinstance(w, ClearableFileInput):
                w.attrs["class"] = (w.attrs.get("class", "") + " form-control").strip()

        if self.is_bound:
            for fname in self.errors:
                try:
                    self.fields[fname].widget.attrs["class"] += " is-invalid"
                except Exception:
                    pass

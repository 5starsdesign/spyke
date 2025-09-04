from django import forms
from django.forms import inlineformset_factory
from properties.models import ExchangeOffer, ExchangeOfferImage, Wish, PROPERTY_TYPES
from accounts.models import Profile

# ------- Eigen woning -------
class MemberOwnForm(forms.ModelForm):
    class Meta:
        model = ExchangeOffer
        exclude = ("id","created_at","updated_at","member","is_published","my_tenure","my_price")
        labels = {
            "my_title": "Titel",
            "my_address": "Straat",
            "my_postcode": "Postcode",
            "my_city": "Plaats",
            "my_province": "Provincie",
            "my_property_type": "Type woning",
            "my_living_area": "Woonoppervlakte (m²)",
            "my_rooms": "Aantal kamers",
            "my_bedrooms": "Aantal slaapkamers",
            "my_floor": "Verdieping",
            "my_floors": "Aantal verdiepingen",
            "my_rent": "Huurprijs (€)",
            "my_garden": "Tuin",
            "my_balcony": "Balkon",
            "my_terrace": "Terras",
            "my_storage": "Berging",
            "shed": "Schuur",
            "my_parking_garage": "Garage",
            "my_near_shops": "Dichtbij winkels",
            "my_near_schools": "Dichtbij scholen",
            "my_ov": "Dichtbij OV",
            "wheelchair": "Rolstoeltoegankelijk",
            "pets_allowed": "Huisdieren toegestaan",
            "new_build": "Nieuwbouw",
            "my_cover": "Hoofdfoto",
            "my_floorplan": "Plattegrond",
            "my_description": "Beschrijving",
        }
        widgets = {
            "my_title": forms.TextInput(attrs={"class":"form-control","placeholder":"Bijv. Ruim 3-kamer appartement"}),
            "my_address": forms.TextInput(attrs={"class":"form-control","placeholder":"Straat + huisnummer"}),
            "my_postcode": forms.TextInput(attrs={"class":"form-control","placeholder":"1234 AB"}),
            "my_city": forms.TextInput(attrs={"class":"form-control"}),
            "my_province": forms.TextInput(attrs={"class":"form-control"}),
            "my_property_type": forms.Select(attrs={"class":"form-select"}),
            "my_living_area": forms.NumberInput(attrs={"class":"form-control","min":"0"}),
            "my_rooms": forms.NumberInput(attrs={"class":"form-control","min":"0"}),
            "my_bedrooms": forms.NumberInput(attrs={"class":"form-control","min":"0"}),
            "my_floor": forms.NumberInput(attrs={"class":"form-control","min":"0"}),
            "my_floors": forms.NumberInput(attrs={"class":"form-control","min":"0"}),
            "my_rent": forms.NumberInput(attrs={"class":"form-control","step":"0.01","min":"0"}),
            "my_description": forms.Textarea(attrs={"class":"form-control","rows":5,"placeholder":"Beschrijf de woning…"}),
            "my_cover": forms.ClearableFileInput(attrs={"class":"form-control"}),
            "my_floorplan": forms.ClearableFileInput(attrs={"class":"form-control"}),
            "my_garden": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "my_balcony": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "my_terrace": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "my_storage": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "shed": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "my_parking_garage": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "my_near_shops": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "my_near_schools": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "my_ov": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "wheelchair": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "pets_allowed": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "new_build": forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }

ExchangeImageFormSet = inlineformset_factory(
    ExchangeOffer, ExchangeOfferImage,
    fields=("image",), extra=5, can_delete=True,
    widgets={"image": forms.ClearableFileInput(attrs={"class":"form-control"})}
)

# ------- Wens -------
class WishForm(forms.ModelForm):
    class Meta:
        model = Wish
        exclude = ("user",)
        labels = {
            "city": "Gewenste plaats(en) / regio",
            "type": "Type woning",
            "price": "Max. huurprijs (€)",
            "size": "Minimaal woonoppervlakte (m²)",
            "rooms": "Minimaal aantal kamers",
            "bedrooms": "Minimaal aantal slaapkamers",
            "want_garden": "Tuin",
            "want_balcony": "Balkon",
            "want_terrace": "Terras",
            "want_storage": "Berging",
            "want_shed": "Schuur",
            "want_garage": "Garage",
            "want_near_shops": "Dichtbij winkels",
            "want_near_schools": "Dichtbij scholen",
            "want_near_ov": "Dichtbij OV",
            "want_ground_floor": "Gelijkvloers",
            "want_lift": "Lift",
            "want_wheelchair": "Rolstoeltoegankelijk",
            "want_pets_allowed": "Huisdieren toegestaan",
            "features": "Extra wensen",
        }
        widgets = {
            "city": forms.TextInput(attrs={"class":"form-control","placeholder":"Bijv. Amsterdam, Utrecht / Randstad"}),
            "type": forms.Select(choices=PROPERTY_TYPES, attrs={"class":"form-select"}),
            "price": forms.NumberInput(attrs={"class":"form-control","min":"0","step":"0.01"}),
            "size": forms.NumberInput(attrs={"class":"form-control","min":"0"}),
            "rooms": forms.NumberInput(attrs={"class":"form-control","min":"0"}),
            "bedrooms": forms.NumberInput(attrs={"class":"form-control","min":"0"}),
            "want_garden": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "want_balcony": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "want_terrace": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "want_storage": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "want_shed": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "want_garage": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "want_near_shops": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "want_near_schools": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "want_near_ov": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "want_ground_floor": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "want_lift": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "want_wheelchair": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "want_pets_allowed": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "features": forms.Textarea(attrs={"class":"form-control","rows":3,"placeholder":"Eventuele extra wensen…"}),
        }

# ------- Profiel -------
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar","address","postcode","city","province")
        labels = {
            "avatar": "Profielfoto",
            "address": "Adres",
            "postcode": "Postcode",
            "city": "Plaats",
            "province": "Provincie",
        }
        widgets = {
            "avatar": forms.ClearableFileInput(attrs={"class":"form-control"}),
            "address": forms.TextInput(attrs={"class":"form-control","placeholder":"Straat + huisnummer"}),
            "postcode": forms.TextInput(attrs={"class":"form-control","placeholder":"1234 AB"}),
            "city": forms.TextInput(attrs={"class":"form-control"}),
            "province": forms.TextInput(attrs={"class":"form-control"}),
        }

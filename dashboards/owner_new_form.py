from django import forms
from django.forms.widgets import ClearableFileInput
from properties.models import MarketListing

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True


class MultiFileField(forms.FileField):
    def clean(self, data, initial=None):
        # accepteer meerdere bestanden; valideer individueel
        if not data:
            return []
        if isinstance(data, (list, tuple)):
            cleaned = []
            for f in data:
                if f:
                    cleaned.append(super().clean(f, initial))
            return cleaned
        return [super().clean(data, initial)]

class OwnerNewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from django.forms.widgets import TextInput, NumberInput, URLInput, EmailInput, DateInput, Textarea, Select, CheckboxInput, RadioSelect, ClearableFileInput
        except Exception:
            pass
        for name, field in self.fields.items():
            w = field.widget
            cls = getattr(w, 'attrs', {}).get('class','')
            if hasattr(w, 'input_type') and w.input_type in ('text','number','url','email','date'): w.attrs['class'] = (cls+' form-control').strip()
            elif w.__class__.__name__ in ('Textarea',): w.attrs['class'] = (cls+' form-control').strip()
            elif w.__class__.__name__ in ('Select',): w.attrs['class'] = (cls+' form-select').strip()
            elif w.__class__.__name__ in ('CheckboxInput',): w.attrs['class'] = (cls+' form-check-input').strip()
            elif w.__class__.__name__ in ('RadioSelect',): w.attrs['class'] = (cls+' form-check-input').strip()
            elif w.__class__.__name__ in ('ClearableFileInput',): w.attrs['class'] = (cls+' form-control').strip()
        # foutvelden rood markeren
        if self.is_bound:
            for fname in self.errors:
                try:
                    self.fields[fname].widget.attrs['class'] += ' is-invalid'
                except Exception:
                    pass


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # generieke Bootstrap classes
        for name, field in self.fields.items():
            w = field.widget
            try:
                # tekst/nummer/url/email/datum/textarea
                from django.forms.widgets import TextInput, NumberInput, URLInput, EmailInput, DateInput, Textarea, Select, CheckboxInput, RadioSelect, ClearableFileInput
                if isinstance(w, (TextInput, NumberInput, URLInput, EmailInput, DateInput, Textarea)):
                    w.attrs['class'] = (w.attrs.get('class','') + ' form-control').strip()
                elif isinstance(w, Select):
                    w.attrs['class'] = (w.attrs.get('class','') + ' form-select').strip()
                elif isinstance(w, (CheckboxInput,)):
                    w.attrs['class'] = (w.attrs.get('class','') + ' form-check-input').strip()
                elif isinstance(w, (RadioSelect,)):
                    w.attrs['class'] = (w.attrs.get('class','') + ' form-check-input').strip()
                elif isinstance(w, (ClearableFileInput,)):
                    w.attrs['class'] = (w.attrs.get('class','') + ' form-control').strip()
            except Exception:
                pass
    # Algemeen
    listing_kind = forms.ChoiceField(
        choices=(("HUUR","Huur"),("KOOP","Koop")),
        widget=forms.RadioSelect, label="Aanbodtype"
    )
    title = forms.CharField(label="Titel / korte omschrijving")
    available_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type":"date"}), label="Beschikbaar per")
    status_active = forms.BooleanField(required=False, initial=True, label="Status: actief (uit = concept)")

    # Locatie
    street = forms.CharField(label="Straat", required=False)
    house_no = forms.CharField(label="Huisnr", required=False)
    house_add = forms.CharField(label="Toevoeging", required=False)
    postcode = forms.CharField(label="Postcode")
    city = forms.CharField(label="Plaats")
    province = forms.CharField(label="Provincie")
    district = forms.CharField(label="Buurt/wijk", required=False)

    # Objectgegevens
    property_type = forms.ChoiceField(choices=MarketListing._meta.get_field("property_type").choices, label="Type woning")
    build_year = forms.IntegerField(required=False, label="Bouwjaar", min_value=1000, max_value=3000)
    living_area = forms.IntegerField(label="Woonoppervlakte (m²)", min_value=0)
    lot_area = forms.IntegerField(required=False, label="Perceeloppervlakte (m²)", min_value=0)
    rooms = forms.IntegerField(label="Aantal kamers", min_value=0)
    bedrooms = forms.IntegerField(required=False, label="Aantal slaapkamers", min_value=0)
    bathrooms = forms.IntegerField(required=False, label="Aantal badkamers", min_value=0)
    floors = forms.IntegerField(required=False, label="Aantal verdiepingen", min_value=0)
    energy_label = forms.CharField(required=False, label="Energielabel")

    # Extra specificaties
    heating = forms.CharField(required=False, label="Verwarming (keuze)")
    isolation_dak = forms.BooleanField(required=False, label="Isolatie dak")
    isolation_muur = forms.BooleanField(required=False, label="Isolatie muur")
    isolation_vloer = forms.BooleanField(required=False, label="Isolatie vloer")
    isolation_glas = forms.BooleanField(required=False, label="Isolatie glas")

    # Kenmerken
    garden = forms.BooleanField(required=False, label="Tuin")
    balcony = forms.BooleanField(required=False, label="Balkon")
    terrace = forms.BooleanField(required=False, label="Terras")
    storage = forms.BooleanField(required=False, label="Berging")
    shed = forms.BooleanField(required=False, label="Schuur")
    parking_garage = forms.BooleanField(required=False, label="Garage")
    parking_spot = forms.BooleanField(required=False, label="Eigen parkeerplaats")
    near_shops = forms.BooleanField(required=False, label="Dichtbij winkels")
    near_schools = forms.BooleanField(required=False, label="Dichtbij scholen")
    near_ov = forms.BooleanField(required=False, label="Dichtbij OV")
    ground_floor = forms.BooleanField(required=False, label="Gelijkvloers")
    elevator = forms.BooleanField(required=False, label="Lift")
    wheelchair_accessible = forms.BooleanField(required=False, label="Rolstoeltoegankelijk")
    solar_panels = forms.BooleanField(required=False, label="Zonnepanelen")
    dormer = forms.BooleanField(required=False, label="Dakkapel")
    extension = forms.BooleanField(required=False, label="Uitbouw")

    # KOOP / HUUR (gedeelde prijsinput)
    price = forms.DecimalField(label="Vraagprijs (€) / Huurprijs (€)", max_digits=10, decimal_places=2)
    kk_von = forms.ChoiceField(choices=(("KK","k.k."),("VON","v.o.n.")), required=False, widget=forms.RadioSelect, label="Kosten")
    vve_service = forms.DecimalField(required=False, max_digits=8, decimal_places=2, label="Servicekosten VvE p/m")
    condition_state = forms.CharField(required=False, label="Onderhoudsstaat")

    service_costs = forms.DecimalField(required=False, max_digits=8, decimal_places=2, label="Servicekosten p/m")
    deposit = forms.DecimalField(required=False, max_digits=10, decimal_places=2, label="Waarborgsom (€)")
    rental_min = forms.IntegerField(required=False, min_value=0, label="Huurtermijn min. (mnd)")
    rental_max = forms.IntegerField(required=False, min_value=0, label="Huurtermijn max. (mnd)")
    income_req = forms.CharField(required=False, label="Inkomenseis")
    pets_allowed = forms.BooleanField(required=False, label="Huisdieren toegestaan")
    smoking_allowed = forms.BooleanField(required=False, label="Roken toegestaan")
    suitable_for = forms.CharField(required=False, label="Geschikt voor (bv. studenten/gezin/expats)")

    # Media
    cover = forms.ImageField(required=False, label="Coverfoto")
    gallery = MultiFileField(required=False, widget=MultiFileInput(attrs={"multiple": True}), label="Galerij (meerdere)")
    floorplan = forms.ImageField(required=False, label="Plattegrond")
    video_url = forms.URLField(required=False, label="Video/360-tour URL")

    # Contact
    contact_first = forms.CharField(required=False, label="Voornaam eigenaar")
    contact_last = forms.CharField(required=False, label="Achternaam eigenaar")
    contact_email = forms.EmailField(required=False, label="E-mail")
    contact_phone = forms.CharField(required=False, label="Telefoon")
    contact_pref_mail = forms.BooleanField(required=False, label="Contact per mail")
    contact_pref_phone = forms.BooleanField(required=False, label="Contact per telefoon")
    viewing_slots = forms.CharField(required=False, label="Bezichtigingsmomenten")

    # Publicatie
    show_exact_address = forms.BooleanField(required=False, initial=True, label="Toon exact adres")
    seo_title = forms.CharField(required=False, label="SEO title")
    seo_description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows":2}), label="SEO description")

    class Meta:
        model = MarketListing
        fields = ("slug",)

    def clean(self):
        data = super().clean()
        kind = data.get("listing_kind")
        if (data.get("price") in (None, "")):
            self.add_error("price", "Huurprijs is verplicht." if kind == "HUUR" else "Vraagprijs is verplicht.")
        return data

    def to_address(self):
        parts = [self.cleaned_data.get("street") or ""]
        tail = " ".join(x for x in [(self.cleaned_data.get("house_no") or ""), (self.cleaned_data.get("house_add") or "")] if x).strip()
        if tail: parts.append(tail)
        return ", ".join([p for p in parts if p])
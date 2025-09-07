from django import forms

from accounts.models import AgencyProfile


class AgencyProfileForm(forms.ModelForm):
    class Meta:
        model = AgencyProfile
        exclude = (
            "user",
            "slug",
            "created_at",
            "updated_at",
        )
        widgets = {
            "company_legal_name": forms.TextInput(attrs={"class": "form-control"}),
            "company_trade_name": forms.TextInput(attrs={"class": "form-control"}),
            "kvk_number": forms.TextInput(attrs={"class": "form-control"}),
            "vat_number": forms.TextInput(attrs={"class": "form-control"}),
            "reg_address": forms.TextInput(attrs={"class": "form-control"}),
            "reg_postcode": forms.TextInput(attrs={"class": "form-control"}),
            "reg_city": forms.TextInput(attrs={"class": "form-control"}),
            "reg_province": forms.TextInput(attrs={"class": "form-control"}),
            "post_address": forms.TextInput(attrs={"class": "form-control"}),
            "post_postcode": forms.TextInput(attrs={"class": "form-control"}),
            "post_city": forms.TextInput(attrs={"class": "form-control"}),
            "post_province": forms.TextInput(attrs={"class": "form-control"}),
            "primary_email": forms.EmailInput(attrs={"class": "form-control"}),
            "primary_phone": forms.TextInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "hq_opening_hours": forms.TextInput(attrs={"class": "form-control"}),
            "extra_branches": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Adres | Tel | Openingstijden",
                }
            ),
            "lead_contacts": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Naam | Rol | E-mail | Tel",
                }
            ),
            "brand_primary_color": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "#0d6efd"}
            ),
            "brand_secondary_color": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "#6c757d"}
            ),
            "brand_accent_color": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "#198754"}
            ),
            "brand_style": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "linkedin_url": forms.URLInput(attrs={"class": "form-control"}),
            "facebook_url": forms.URLInput(attrs={"class": "form-control"}),
            "instagram_url": forms.URLInput(attrs={"class": "form-control"}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "cover": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "published": "Publiek zichtbaar",
            "logo": "Logo",
            "cover": "Omslagafbeelding",
        }

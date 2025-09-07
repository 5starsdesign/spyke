from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.templatetags.static import static
from django.utils import timezone
from django.utils.text import slugify

# Keuzes
PROPERTY_TYPES = [
    ("appartement", "Appartement"),
    ("eengezinswoning", "Eengezinswoning"),
    ("rijtjeshuis", "Rijtjeshuis"),
    ("vrijstaand", "Vrijstaand"),
    ("studio", "Studio"),
    ("tussenwoning", "Tussenwoning"),
    ("hoekwoning", "Hoekwoning"),
    ("villa", "Villa"),
]
ENERGY_LABELS = [
    ("A++++", "A++++"),
    ("A+++", "A+++"),
    ("A++", "A++"),
    ("A+", "A+"),
    ("A", "A"),
    ("B", "B"),
    ("C", "C"),
    ("D", "D"),
    ("E", "E"),
    ("F", "F"),
    ("G", "G"),
    ("ONBEKEND", "Onbekend"),
]
FINISH_CHOICES = [
    ("KAAL", "Kaal"),
    ("GESTOFFEERD", "Gestoffeerd"),
    ("GEMEUBILEERD", "Gemeubileerd"),
]
RENTAL_TERM_CHOICES = [
    ("BEPAALDE_TIJD", "Bepaalde tijd"),
    ("ONBEPAALDE_TIJD", "Onbepaalde tijd"),
]


class Meta:
    ordering = ["-created_at"]


class Meta:
    ordering = ["-created_at"]


class Timestamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ── Agency/Owner listing ────────────────────────────────────────────────────────
class MarketListing(Timestamped):
    class Meta:
        verbose_name = "Woning (makelaar)"
        verbose_name_plural = "Woningen (makelaars)"

    class Meta:
        verbose_name = "Woning (makelaar)"
        verbose_name_plural = "Woningen (makelaars)"

    K_HUUR = "HUUR"
    K_KOOP = "KOOP"
    KIND_CHOICES = [(K_HUUR, "Huur"), (K_KOOP, "Koop")]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings"
    )

    # Basis
    title = models.CharField(
        max_length=200, blank=True
    )  # optioneel; adres kan titel vervangen
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    address = models.CharField(max_length=255)
    postcode = models.CharField(max_length=16, blank=True)
    city = models.CharField(max_length=120)
    province = models.CharField(max_length=64, blank=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    build_year = models.PositiveIntegerField(blank=True, null=True)

    # Vaste kenmerken
    living_area = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], help_text="m²"
    )
    lot_area = models.PositiveIntegerField(
        blank=True, null=True, help_text="Perceel m²"
    )
    rooms = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    bedrooms = models.PositiveIntegerField(blank=True, null=True)
    bathrooms = models.PositiveIntegerField(blank=True, null=True)
    floors = models.PositiveIntegerField(blank=True, null=True)

    # Koop/Huur keuze + prijs
    listing_kind = models.CharField(max_length=8, choices=KIND_CHOICES, default=K_KOOP)
    # 'price' = vraagprijs (KOOP) of maandhuur (HUUR)
    price = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )

    # Voorzieningen / kenmerken
    garden = models.BooleanField(default=False)
    balcony = models.BooleanField(default=False)
    terrace = models.BooleanField(default=False)
    roof_terrace = models.BooleanField(default=False)

    storage = models.BooleanField(default=False)
    shed = models.BooleanField(default=False)
    parking_garage = models.BooleanField(default=False)
    parking_spot = models.BooleanField(default=False)

    energy_label = models.CharField(
        max_length=10, choices=ENERGY_LABELS, default="ONBEKEND"
    )
    solar_panels = models.BooleanField(default=False)
    heat_pump = models.BooleanField(default=False)

    wheelchair_accessible = models.BooleanField(default=False)
    elevator = models.BooleanField(default=False)
    new_build = models.BooleanField(default=False)

    # HUUR-specifiek
    service_costs = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    deposit = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    available_from = models.DateField(blank=True, null=True)
    rental_term = models.CharField(
        max_length=20, choices=RENTAL_TERM_CHOICES, blank=True
    )
    finish = models.CharField(max_length=20, choices=FINISH_CHOICES, blank=True)
    pets_allowed = models.BooleanField(default=False)
    smoking_allowed = models.BooleanField(default=False)
    suitable_for = models.TextField(
        blank=True, help_text="CSV: studenten, gezin, expats"
    )

    # Optioneel
    description = models.TextField(blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = (
                f"{(self.title or self.address or 'woning')}-{self.city}".lower()
                .strip()
                .replace(" ", "-")
            )
            base = base[:200] or "listing"
            slug = base
            i = 2
            while MarketListing.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"[:220]
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        kind = self.get_listing_kind_display() if self.listing_kind else "Woning"
        return f"{kind}: {self.title or self.address} ({self.city})"

    @property
    def cover_url(self):
        img = self.images.first()
        try:
            return (
                img.image.url
                if img and getattr(img, "image", None)
                else static("img/placeholder_listing.svg")
            )
        except Exception:
            return static("img/placeholder_listing.svg")


class MarketListingImage(models.Model):
    class Meta:
        verbose_name = "Woning (makelaar)"
        verbose_name_plural = "Woningen (makelaars)"

    class Meta:
        verbose_name = "Woning (makelaar)"
        verbose_name_plural = "Woningen (makelaars)"

    listing = models.ForeignKey(
        MarketListing, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="listing_images/")


# ── (Member-ruil/wens kunnen hier blijven bestaan als jouw project die heeft;
#     we laten ze bewust weg om agency los te houden.)

# ==== RUILWONINGEN (Members) ====
from django.core.validators import MinValueValidator as _MV


class ExchangeOffer(Timestamped):
    def save(self, *args, **kwargs):
        from .models_exchangeoffer_patch import patched_exchangeoffer_save

        return patched_exchangeoffer_save(self, *args, **kwargs)
        from .models_exchangeoffer_patch import patched_exchangeoffer_save

        return patched_exchangeoffer_save(self, *args, **kwargs)

        if not self.slug:

            from django.utils.text import slugify

            base = slugify(self.my_title or f"woning-{self.pk or ''}") or "woning"

            slug = base[:180]

            i = 2

            from properties.models import ExchangeOffer

            while ExchangeOffer.objects.filter(slug=slug).exclude(pk=self.pk).exists():

                slug = f"{base}-{i}"[:200]
                i += 1

            self.slug = slug

        super().save(*args, **kwargs)

    slug = models.SlugField(max_length=200, unique=True, blank=True)

    class Meta:
        verbose_name = "Woningruil (member)"
        verbose_name_plural = "Woningruilen (members)"

    class Meta:
        verbose_name = "Woningruil (member)"
        verbose_name_plural = "Woningruilen (members)"

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exchange_offers",
    )
    my_title = models.CharField(max_length=200, blank=False)
    my_address = models.CharField(max_length=255, blank=True, null=True)
    my_postcode = models.CharField(max_length=16, blank=True, null=True)
    my_city = models.CharField(max_length=120, blank=True)
    my_province = models.CharField(max_length=64, blank=True, null=True)
    TENURE_CHOICES = [("HUUR", "Huur"), ("KOOP", "Koop")]
    my_property_type = models.CharField(
        max_length=20, choices=PROPERTY_TYPES, blank=True
    )
    my_tenure = models.CharField(
        max_length=4, choices=TENURE_CHOICES, blank=True, null=True
    )
    my_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    my_rent = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    my_description = models.TextField(blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    my_living_area = models.PositiveIntegerField(
        blank=True, null=True, validators=[_MV(1)]
    )
    my_rooms = models.PositiveIntegerField(blank=True, null=True, validators=[_MV(1)])
    my_bedrooms = models.PositiveIntegerField(
        blank=True, null=True, validators=[_MV(0)]
    )
    my_floor = models.IntegerField(blank=True, null=True)
    my_floors = models.PositiveIntegerField(blank=True, null=True, validators=[_MV(0)])
    my_balcony = models.BooleanField(default=False)
    my_terrace = models.BooleanField(default=False)
    my_garden = models.BooleanField(default=False)
    my_storage = models.BooleanField(default=False)
    shed = models.BooleanField(default=False)
    my_attic = models.BooleanField(default=False)
    my_cellar = models.BooleanField(default=False)
    my_parking_street = models.BooleanField(default=False)
    my_parking_garage = models.BooleanField(default=False)
    my_parking_private = models.BooleanField(default=False)
    my_near_shops = models.BooleanField(default=False)
    my_near_schools = models.BooleanField(default=False)
    my_ov = models.BooleanField(default=False)
    wheelchair = models.BooleanField(default=False)
    pets_allowed = models.BooleanField(default=False)
    new_build = models.BooleanField(default=False)
    my_cover = models.ImageField(upload_to="exchange_covers/", blank=True, null=True)
    my_floorplan = models.ImageField(
        upload_to="exchange_floorplans/", blank=True, null=True
    )
    want_city = models.CharField(max_length=120, blank=True)
    want_property_type = models.CharField(
        max_length=20, choices=PROPERTY_TYPES, blank=True
    )
    want_min_area = models.PositiveIntegerField(
        blank=True, null=True, validators=[_MV(1)]
    )
    want_min_rooms = models.PositiveIntegerField(
        blank=True, null=True, validators=[_MV(1)]
    )
    want_balcony = models.BooleanField(default=False)
    want_terrace = models.BooleanField(default=False)
    want_garden = models.BooleanField(default=False)
    want_storage = models.BooleanField(default=False)
    want_attic = models.BooleanField(default=False)
    want_cellar = models.BooleanField(default=False)
    want_parking_private = models.BooleanField(default=False)
    want_ov = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["-id"]

    def clean(self):
        if self.is_published:
            from django.core.exceptions import ValidationError

            errs = {}
            for f in [
                "my_title",
                "my_city",
                "my_property_type",
                "my_living_area",
                "my_rooms",
            ]:
                if not getattr(self, f):
                    errs[f] = "Veld is verplicht bij publiceren."
            if errs:
                raise ValidationError(errs)

    def __str__(self):
        return f"Woningruil: {self.my_title or 'concept'} ({self.member})"


# --- Wish model toegevoegd ---
PROPERTY_TYPES = [
    ("appartement", "Appartement"),
    ("eengezinswoning", "Eengezinswoning"),
    ("villa", "Villa"),
    ("studio", "Studio"),
    ("ander", "Anders"),
]


class Wish(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField("Gewenste stad", max_length=120)
    province = models.CharField("Gewenste provincie", max_length=64, blank=True)
    property_type = models.CharField(
        "Type woning", max_length=20, choices=PROPERTY_TYPES
    )
    min_area = models.PositiveIntegerField(
        "Minimale woonoppervlakte (m²)", blank=True, null=True
    )
    min_rooms = models.PositiveIntegerField(
        "Minimaal aantal kamers", blank=True, null=True
    )
    balcony = models.BooleanField("Balkon gewenst", default=False)
    terrace = models.BooleanField("Terras gewenst", default=False)
    garden = models.BooleanField("Tuin gewenst", default=False)
    storage = models.BooleanField("Berging gewenst", default=False)
    attic = models.BooleanField("Zolder gewenst", default=False)
    cellar = models.BooleanField("Kelder gewenst", default=False)
    parking_private = models.BooleanField("Parkeerplaats gewenst", default=False)
    ov = models.BooleanField("Dichtbij OV gewenst", default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Wenswoning"
        verbose_name_plural = "Wenswoningen"

    def __str__(self):
        return f"Wens van {self.user.username} ({self.city}, {self.property_type})"


class ExchangeOfferImage(models.Model):
    offer = models.ForeignKey(
        "ExchangeOffer", related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="exchange_offers/")
    alt_text = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Foto bij woningruil"
        verbose_name_plural = "Foto’s bij woningruilen"

    def __str__(self):
        return f"Foto van {self.offer.my_title or 'woning'}"

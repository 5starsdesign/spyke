from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=16, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    province = models.CharField(max_length=64, blank=True, null=True)
    premium = models.BooleanField(default=False)

    def __str__(self):
        return f"Profiel van {self.user}"

    @property
    def is_premium(self):
        premium_emails = getattr(settings, "PREMIUM_EMAILS", [])
        return bool(self.premium or (self.user and self.user.email in premium_emails))

class AgencyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agency_profile")
    company_legal_name = models.CharField("Bedrijfsnaam (juridisch)", max_length=200, blank=True)
    company_trade_name = models.CharField("Handelsnaam", max_length=200, blank=True)
    kvk_number = models.CharField("KVK-nummer", max_length=32, blank=True)
    vat_number = models.CharField("BTW-nummer", max_length=32, blank=True)

    reg_address = models.CharField("Vestigingsadres", max_length=255, blank=True)
    reg_postcode = models.CharField("Postcode", max_length=16, blank=True)
    reg_city = models.CharField("Plaats", max_length=120, blank=True)
    reg_province = models.CharField("Provincie", max_length=64, blank=True)

    post_address = models.CharField("Postadres", max_length=255, blank=True)
    post_postcode = models.CharField("Postcode (post)", max_length=16, blank=True)
    post_city = models.CharField("Plaats (post)", max_length=120, blank=True)
    post_province = models.CharField("Provincie (post)", max_length=64, blank=True)

    primary_email = models.EmailField("Primair e-mail", blank=True)
    primary_phone = models.CharField("Telefoon", max_length=64, blank=True)
    website = models.URLField("Website", blank=True)

    hq_opening_hours = models.CharField("Openingstijden (hoofdkantoor)", max_length=200, blank=True)
    extra_branches = models.TextField("Extra vestigingen (één per regel: adres | tel | openingstijden)", blank=True)
    lead_contacts = models.TextField("Contactpersonen leads (één per regel: naam | rol | e-mail | tel)", blank=True)

    logo = models.ImageField(upload_to="agency/logo/", blank=True, null=True)
    cover = models.ImageField(upload_to="agency/cover/", blank=True, null=True)
    brand_primary_color = models.CharField(max_length=7, blank=True, default="#0d6efd")
    brand_secondary_color = models.CharField(max_length=7, blank=True, default="#6c757d")
    brand_accent_color = models.CharField(max_length=7, blank=True, default="#198754")
    brand_style = models.TextField("Kleuren/merkstijl (notities)", blank=True)
    bio = models.TextField("Korte bio/omschrijving", blank=True)
    linkedin_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)

    slug = models.SlugField(max_length=220, unique=True, blank=True)
    published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.company_trade_name or self.company_legal_name or (self.user.get_username() if self.user_id else "agency")
            from django.utils.text import slugify
            base = slugify(base)[:200] or "agency"
            slug = base; i=2
            while AgencyProfile.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"[:220]; i+=1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.company_trade_name or self.company_legal_name or f"Agency {self.pk}"


import io
import random

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image

from accounts.models import Profile
from properties.models import ExchangeOffer, MarketListing, MarketListingImage


def png(color=(180, 180, 180), size=(800, 450)):
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return ContentFile(buf.getvalue(), name="img.png")


class Command(BaseCommand):
    help = "Voegt demo-gebruikers en 8 listings toe (4 ruil, 4 huur)."

    def handle(self, *args, **opts):
        def mkuser(u, role):
            user, _ = User.objects.get_or_create(
                username=u, defaults={"email": f"{u}@ex.com"}
            )
            prof, _ = Profile.objects.get_or_create(user=user, defaults={"role": role})
            prof.role = role
            prof.save()
            return user

        m1 = mkuser("lid1", Profile.ROLE_MEMBER)
        m2 = mkuser("lid2", Profile.ROLE_MEMBER)
        own = mkuser("owner1", Profile.ROLE_OWNER)
        ag = mkuser("makelaar1", Profile.ROLE_AGENCY)
        ag.profile.company_name = "Top Makelaar"
        ag.profile.save()

        # Huur (4x)
        for i in range(1, 5):
            l, _ = MarketListing.objects.get_or_create(
                title=f"Huurwoning {i}",
                owner=ag,
                defaults=dict(
                    city=random.choice(
                        ["Amsterdam", "Rotterdam", "Utrecht", "Den Haag"]
                    ),
                    listing_kind=MarketListing.K_HUUR,
                    property_type="appartement",
                    price=1250 + i * 50,
                    description="Fijne huurwoning met alles in de buurt.",
                    living_area=50 + i * 5,
                    rooms=2 + (i % 3),
                    balcony=True,
                    near_shops=True,
                    ov=True,
                    is_published=True,
                    is_featured=(i <= 2),
                ),
            )
            MarketListingImage.objects.get_or_create(
                listing=l, defaults={"image": png()}
            )

        # Ruil (4x)
        for i, (u, city) in enumerate(
            [(m1, "Utrecht"), (m1, "Rotterdam"), (m2, "Amsterdam"), (m2, "Den Haag")],
            start=1,
        ):
            ExchangeOffer.objects.get_or_create(
                member=u,
                my_title=f"Ruilwoning {i}",
                defaults=dict(
                    my_city=city,
                    my_property_type="appartement",
                    my_rent=900 + i * 25,
                    my_description="Leuke ruilwoning.",
                    my_living_area=45 + i * 5,
                    my_rooms=2 + (i % 2),
                    my_balcony=True,
                    my_ov=True,
                    want_city=random.choice(["Amsterdam", "Utrecht", "Rotterdam"]),
                    want_property_type="appartement",
                    want_min_area=40,
                    want_min_rooms=2,
                    want_garden=False,
                    is_published=True,
                ),
            )

        self.stdout.write(self.style.SUCCESS("Demo data klaar."))

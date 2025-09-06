from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile

class Command(BaseCommand):
    help = "Maak ontbrekende Profile records voor bestaande Users"

    def handle(self, *args, **options):
        count = 0
        for user in User.objects.all():
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={"role": Profile.ROLE_MEMBER}
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f"Profile aangemaakt voor {user.username} (MEMBER)"))
        self.stdout.write(self.style.SUCCESS(f"Totaal {count} nieuwe profiles aangemaakt."))

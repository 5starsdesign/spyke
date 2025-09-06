#!/bin/bash
set -e

BACKUP_DIR=~/bakkie-op
BACKUP_FILE="$BACKUP_DIR/setup-profiles_$(date +%F_%H-%M-%S).tar.gz"

echo "📦 Back-up maken naar $BACKUP_FILE..."
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_FILE" accounts dashboards config

echo "📝 Controleren of OwnerProfile model bestaat..."
if ! grep -q "class OwnerProfile" accounts/models.py; then
  echo "➕ Toevoegen van OwnerProfile model aan accounts/models.py..."
  cat >> accounts/models.py <<'EOF'

class OwnerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owner_profile"
    )
    display_name = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=255, blank=True)
    postcode = models.CharField(max_length=16, blank=True)
    city = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=64, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or f"Owner {self.user.username}"
EOF
fi

echo "⚙️ Migraties genereren en toepassen..."
docker compose exec -T web python manage.py makemigrations accounts
docker compose exec -T web python manage.py migrate

echo "👤 Ontbrekende basisprofielen (Profile) aanmaken..."
docker compose exec -T web python manage.py create_missing_profiles

echo "🏠 Ontbrekende OwnerProfiles aanmaken..."
docker compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
from accounts.models import Profile, OwnerProfile
created = 0
for u in User.objects.filter(profile__role=Profile.ROLE_OWNER):
    OwnerProfile.objects.get_or_create(user=u)
    created += 1
print(f'OwnerProfiles gecontroleerd/ingevoegd voor {created} gebruikers')
"

echo "🏢 Ontbrekende AgencyProfiles aanmaken..."
docker compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
from accounts.models import Profile, AgencyProfile
created = 0
for u in User.objects.filter(profile__role=Profile.ROLE_AGENCY):
    AgencyProfile.objects.get_or_create(user=u)
    created += 1
print(f'AgencyProfiles gecontroleerd/ingevoegd voor {created} gebruikers')
"

echo "✅ Klaar!"

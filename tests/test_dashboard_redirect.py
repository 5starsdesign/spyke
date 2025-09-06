import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profile

@pytest.mark.django_db
@pytest.mark.parametrize("role,expected_url", [
    (Profile.ROLE_MEMBER, "member_home"),
    (Profile.ROLE_OWNER, "owner_home"),
    (Profile.ROLE_AGENCY, "agency_home"),
])
def test_my_dashboard_redirect(client, role, expected_url):
    user = User.objects.create_user(username=role.lower(), password="test123")
    Profile.objects.create(user=user, role=role)

    client.login(username=user.username, password="test123")

    response = client.get(reverse("my_dashboard"))
    assert response.status_code == 302
    assert response.url == reverse(expected_url)


@pytest.mark.django_db
def test_my_dashboard_redirect_no_role(client):
    user = User.objects.create_user(username="norole", password="test123")
    Profile.objects.create(user=user, role=None)

    client.login(username="norole", password="test123")

    response = client.get(reverse("my_dashboard"))
    assert response.status_code == 302
    assert response.url == "/"

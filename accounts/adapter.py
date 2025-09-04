from allauth.account.adapter import DefaultAccountAdapter
from accounts.models import Profile
class RoleAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit)
        role = request.POST.get("role") or Profile.ROLE_MEMBER
        try:
            p = user.profile
        except Profile.DoesNotExist:
            p = Profile(user=user)
        p.role = role
        p.save()
        return user

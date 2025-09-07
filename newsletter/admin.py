from django.contrib import admin

from .models import Signup


@admin.register(Signup)
class SignupAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at", "ip")
    search_fields = ("email", "user_agent")
    list_filter = ("created_at",)

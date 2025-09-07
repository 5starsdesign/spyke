from django.db import models


class Signup(models.Model):
    email = models.EmailField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Nieuwsbrief"
        verbose_name_plural = "Nieuwsbrieven"

    def __str__(self):
        return f"{self.email} @ {self.created_at:%Y-%m-%d %H:%M}"

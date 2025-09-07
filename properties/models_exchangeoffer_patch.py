from django.db import models
from django.utils.text import slugify


def patched_exchangeoffer_save(self, *args, **kwargs):
    if not self.slug:
        base_slug = slugify(self.my_title or f"woning-{self.pk or ''}") or "woning"
        slug = base_slug
        counter = 1
        Model = type(self)
        while Model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
    super(Model, self).save(*args, **kwargs)

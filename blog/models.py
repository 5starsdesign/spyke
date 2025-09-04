from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]
    def __str__(self): return self.name

class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    class Meta:
        ordering = ["name"]
    def __str__(self): return self.name

class Post(models.Model):
    DRAFT = "DRAFT"; PUBLISHED = "PUBLISHED"
    STATUS_CHOICES = [(DRAFT, "Concept"), (PUBLISHED, "Gepubliceerd")]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    cover = models.ImageField(upload_to="blog/covers/", blank=True, null=True)

    categories = models.ManyToManyField(Category, blank=True, related_name="posts")
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=DRAFT, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # SEO
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    canonical_url = models.URLField(blank=True)
    og_image = models.ImageField(upload_to="blog/og/", blank=True, null=True)

    class Meta:
        ordering = ("-published_at", "-created_at")
        indexes = [models.Index(fields=["status","published_at"])]

    def __str__(self): return self.title
    @property
    def is_published(self): return self.status == self.PUBLISHED
    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        cls = type(self)
        base = slugify((self.slug or self.title) or "")[:200]  # ruimte voor suffix
        if not base:
            base = "post"
        s = base
        i = 2
        # unieke slug afdwingen
        while cls.objects.filter(slug=s).exclude(pk=self.pk).exists():
            s = f"{base}-{i}"
            i += 1
        self.slug = s
        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

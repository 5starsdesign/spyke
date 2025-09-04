from django.contrib import admin
from django import forms
from django.utils.text import slugify
from .models import Post, Category, Tag

class SlugCleanMixin:
    slug_source_field = None  # bv. "title" of "name"
    def clean_slug(self):
        raw = self.cleaned_data.get("slug")
        if not raw:
            if self.slug_source_field:
                raw = self.cleaned_data.get(self.slug_source_field, "")
        s = slugify(raw or "")
        if not s:
            raise forms.ValidationError("Kan geen geldige slug maken. Vul een titel/naam in.")
        return s

class PostAdminForm(forms.ModelForm, SlugCleanMixin):
    slug_source_field = "title"
    class Meta:
        model = Post
        fields = "__all__"

class CategoryAdminForm(forms.ModelForm, SlugCleanMixin):
    slug_source_field = "name"
    class Meta:
        model = Category
        fields = "__all__"

class TagAdminForm(forms.ModelForm, SlugCleanMixin):
    slug_source_field = "name"
    class Meta:
        model = Tag
        fields = "__all__"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    form = TagAdminForm
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("title","status","published_at","author")
    list_filter = ("status","categories","tags")
    search_fields = ("title","excerpt","content")
    date_hierarchy = "published_at"
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories","tags")
    fieldsets = (
        (None, {"fields": ("title","slug","author","excerpt","content","cover","status","published_at")}),
        ("Taxonomie", {"fields": ("categories","tags")}),
        ("SEO", {"fields": ("seo_title","seo_description","canonical_url","og_image")}),
    )

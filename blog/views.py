from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Category, Post, Tag

PAGE_SIZE = 10


def _sidebar_ctx():
    cats = (
        Category.objects.annotate(
            num=Count("posts", filter=Q(posts__status="PUBLISHED"))
        )
        .filter(num__gt=0)
        .order_by("name")
    )
    tags = (
        Tag.objects.annotate(num=Count("posts", filter=Q(posts__status="PUBLISHED")))
        .filter(num__gt=0)
        .order_by("-num", "name")[:30]
    )
    # lijst met unieke maanden (DESC)
    months = Post.objects.filter(status="PUBLISHED", published_at__isnull=False).dates(
        "published_at", "month", order="DESC"
    )
    archives = [{"year": d.year, "month": d.month} for d in months]
    return {"categories": cats, "tags": tags, "archives": archives}


def list_view(request, category_slug=None, tag_slug=None, year=None, month=None):
    qs = Post.objects.filter(status="PUBLISHED")
    if category_slug:
        qs = qs.filter(categories__slug=category_slug)
    if tag_slug:
        qs = qs.filter(tags__slug=tag_slug)
    if year and month:
        qs = qs.filter(published_at__year=year, published_at__month=month)
    paginator = Paginator(
        qs.select_related("author").prefetch_related("categories", "tags"), PAGE_SIZE
    )
    page = paginator.get_page(request.GET.get("page"))
    ctx = {"page_obj": page, **_sidebar_ctx()}
    return render(request, "blog/list.html", ctx)


def detail_view(request, slug):
    obj = get_object_or_404(
        Post.objects.select_related("author").prefetch_related("categories", "tags"),
        slug=slug,
        status="PUBLISHED",
    )
    ctx = {"obj": obj, **_sidebar_ctx()}
    return render(request, "blog/detail.html", ctx)

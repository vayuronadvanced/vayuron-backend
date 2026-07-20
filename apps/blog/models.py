"""
Blog CMS models: posts and categories, admin-authored, publicly readable.
"""

from django.db import models
from django.utils import timezone

from apps.core.models import TimestampedModel
from apps.core.validators import validate_image_file


class BlogCategory(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        # Declaring Meta here replaces (not extends) TimestampedModel.Meta,
        # so ordering must be restated explicitly or pagination becomes
        # nondeterministic (caught by Django's UnorderedObjectListWarning
        # during the Phase 5.4 security/quality review). Alphabetical makes
        # more sense than created_at for a category filter list anyway.
        ordering = ["name"]
        verbose_name_plural = "Blog categories"

    def __str__(self):
        return self.name


class BlogPost(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True)
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="blog_posts",
    )
    excerpt = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    cover_image = models.ImageField(
        upload_to="uploads/images/blog/",
        null=True,
        blank=True,
        validators=validate_image_file,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    published_at = models.DateTimeField(null=True, blank=True)

    def publish(self):
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at"])

    def __str__(self):
        return self.title

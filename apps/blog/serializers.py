from rest_framework import serializers

from .models import BlogCategory, BlogPost


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ["id", "name", "slug"]
        read_only_fields = ["id"]


class BlogPostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (no full content body)."""

    category = BlogCategorySerializer(read_only=True)
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            "id", "title", "slug", "category", "author_name",
            "excerpt", "cover_image", "published_at",
        ]


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Full serializer for a single post (public read) and admin write."""

    class Meta:
        model = BlogPost
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "published_at"]

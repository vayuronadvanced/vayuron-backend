from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrEmployee

from .models import BlogCategory, BlogPost
from .serializers import (
    BlogCategorySerializer,
    BlogPostDetailSerializer,
    BlogPostListSerializer,
)


class BlogCategoryViewSet(viewsets.ModelViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [IsAdminOrEmployee()]


class BlogPostViewSet(viewsets.ModelViewSet):
    """
    Public visitors only ever see status=published posts (enforced in
    get_queryset). Staff can see/manage everything, including drafts.
    """

    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "status"]
    search_fields = ["title", "content"]

    def get_queryset(self):
        qs = BlogPost.objects.select_related("category", "author")
        if self.request.user.is_authenticated and self.request.user.role in (
            "admin",
            "employee",
        ):
            return qs
        return qs.filter(status=BlogPost.Status.PUBLISHED)

    def get_serializer_class(self):
        if self.action == "list":
            return BlogPostListSerializer
        return BlogPostDetailSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [IsAdminOrEmployee()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrEmployee])
    def publish(self, request, slug=None):
        post = self.get_object()
        post.publish()
        return Response(BlogPostDetailSerializer(post).data)

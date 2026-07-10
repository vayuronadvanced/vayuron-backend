from rest_framework.routers import DefaultRouter

from .views import BlogCategoryViewSet, BlogPostViewSet

app_name = "blog"

router = DefaultRouter()
router.register("categories", BlogCategoryViewSet, basename="blog-category")
router.register("posts", BlogPostViewSet, basename="blog-post")

urlpatterns = router.urls

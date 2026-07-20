from rest_framework.routers import DefaultRouter

from .views import UploadedFileViewSet

app_name = "uploads"

router = DefaultRouter()
router.register("", UploadedFileViewSet, basename="uploaded-file")

urlpatterns = router.urls

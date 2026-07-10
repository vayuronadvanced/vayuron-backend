from rest_framework.routers import DefaultRouter

from .views import BusinessEventViewSet

app_name = "analytics"

router = DefaultRouter()
router.register("", BusinessEventViewSet, basename="business-event")

urlpatterns = router.urls

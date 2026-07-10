from rest_framework.routers import DefaultRouter

from .views import JobApplicationViewSet, JobListingViewSet

app_name = "careers"

router = DefaultRouter()
router.register("listings", JobListingViewSet, basename="job-listing")
router.register("applications", JobApplicationViewSet, basename="job-application")

urlpatterns = router.urls

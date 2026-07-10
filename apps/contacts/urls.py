from rest_framework.routers import DefaultRouter

from .views import ContactEnquiryViewSet

app_name = "contacts"

router = DefaultRouter()
router.register("", ContactEnquiryViewSet, basename="contact-enquiry")

urlpatterns = router.urls

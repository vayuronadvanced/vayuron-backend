from rest_framework.routers import DefaultRouter

from .views import ContactEnquiryViewSet, QuestionViewSet

app_name = "contacts"

router = DefaultRouter()
router.register("questions", QuestionViewSet, basename="question")
router.register("", ContactEnquiryViewSet, basename="contact-enquiry")

urlpatterns = router.urls

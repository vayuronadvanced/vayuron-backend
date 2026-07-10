from rest_framework.routers import DefaultRouter

from .views import QuotationRequestViewSet

app_name = "quotations"

router = DefaultRouter()
router.register("", QuotationRequestViewSet, basename="quotation-request")

urlpatterns = router.urls

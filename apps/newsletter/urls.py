from rest_framework.routers import DefaultRouter

from .views import NewsletterCampaignViewSet, NewsletterSubscriberViewSet

app_name = "newsletter"

router = DefaultRouter()
router.register("subscribers", NewsletterSubscriberViewSet, basename="newsletter-subscriber")
router.register("campaigns", NewsletterCampaignViewSet, basename="newsletter-campaign")

urlpatterns = router.urls

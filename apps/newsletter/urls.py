from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import NewsletterCampaignViewSet, NewsletterSubscriberViewSet, UnsubscribeView

app_name = "newsletter"

router = DefaultRouter()
router.register("subscribers", NewsletterSubscriberViewSet, basename="newsletter-subscriber")
router.register("campaigns", NewsletterCampaignViewSet, basename="newsletter-campaign")

urlpatterns = [
    path("unsubscribe/<str:token>/", UnsubscribeView.as_view(), name="unsubscribe"),
] + router.urls

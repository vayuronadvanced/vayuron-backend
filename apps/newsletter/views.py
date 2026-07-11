from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.core.permissions import IsAdminOrEmployee

from .models import NewsletterCampaign, NewsletterSubscriber
from .serializers import (
    NewsletterCampaignSerializer,
    NewsletterSubscriberAdminSerializer,
    NewsletterSubscriberSerializer,
)


class NewsletterSubscriberViewSet(viewsets.ModelViewSet):
    """
    create: open to anyone (public signup form).
    list/retrieve/update/delete: staff only.
    """

    queryset = NewsletterSubscriber.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["is_active"]
    search_fields = ["email"]

    def get_throttles(self):
        if self.action == "create":
            self.throttle_scope = "public_submission"
            return [ScopedRateThrottle()]
        return []

    def get_serializer_class(self):
        if self.action == "create":
            return NewsletterSubscriberSerializer
        return NewsletterSubscriberAdminSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [IsAdminOrEmployee()]


class NewsletterCampaignViewSet(viewsets.ModelViewSet):
    """Staff-only: compose and send newsletters to active subscribers."""

    queryset = NewsletterCampaign.objects.all()
    serializer_class = NewsletterCampaignSerializer
    permission_classes = [IsAdminOrEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["subject"]

    def perform_create(self, serializer):
        serializer.save(sent_by=self.request.user)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        """
        Marks the campaign as sent and stamps recipient_count from the
        current active subscriber list. Actual email dispatch (SMTP/queue)
        is wired in during implementation of the email backend.
        """
        campaign = self.get_object()
        active_count = NewsletterSubscriber.objects.filter(is_active=True).count()
        campaign.status = NewsletterCampaign.Status.SENT
        campaign.sent_at = timezone.now()
        campaign.recipient_count = active_count
        campaign.save(update_fields=["status", "sent_at", "recipient_count"])
        return Response(NewsletterCampaignSerializer(campaign).data)

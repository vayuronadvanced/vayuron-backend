from django.conf import settings
from django.core import signing
from django.core.mail import get_connection, EmailMultiAlternatives
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrEmployee

from .models import NewsletterCampaign, NewsletterSubscriber
from .serializers import (
    NewsletterCampaignSerializer,
    NewsletterSubscriberAdminSerializer,
    NewsletterSubscriberSerializer,
)
from .utils import generate_unsubscribe_token, verify_unsubscribe_token


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
        Actually dispatches the campaign to every active subscriber, one
        email per recipient (never BCC — that would expose every
        subscriber's address to every other recipient). Each email includes
        a personalized, signed unsubscribe link.

        Uses a single reused SMTP connection for the whole batch rather than
        reconnecting per email. Individual send failures are caught so one
        bad address doesn't abort the whole campaign; the response reports
        how many actually succeeded.
        """
        campaign = self.get_object()
        if campaign.status == NewsletterCampaign.Status.SENT:
            return Response(
                {"detail": "This campaign has already been sent."}, status=400
            )

        subscribers = list(NewsletterSubscriber.objects.filter(is_active=True))
        connection = get_connection()
        connection.open()
        sent_count = 0
        try:
            for subscriber in subscribers:
                token = generate_unsubscribe_token(subscriber.id)
                unsubscribe_url = f"{settings.FRONTEND_URL}/newsletter/unsubscribe/{token}"
                body = (
                    f"{campaign.body}\n\n"
                    f"---\n"
                    f"You're receiving this because you subscribed to the "
                    f"Vayuron Advanced Systems newsletter.\n"
                    f"Unsubscribe: {unsubscribe_url}"
                )
                email = EmailMultiAlternatives(
                    subject=campaign.subject,
                    body=body,
                    to=[subscriber.email],
                    connection=connection,
                )
                try:
                    email.send()
                    sent_count += 1
                except Exception:
                    # One bad/rejected address shouldn't sink the whole campaign.
                    continue
        finally:
            connection.close()

        campaign.status = NewsletterCampaign.Status.SENT
        campaign.sent_at = timezone.now()
        campaign.recipient_count = sent_count
        campaign.save(update_fields=["status", "sent_at", "recipient_count"])
        return Response(NewsletterCampaignSerializer(campaign).data)


class UnsubscribeView(APIView):
    """
    Public endpoint backing the emailed unsubscribe link. No auth required
    by design — the signed token itself is the proof of identity, exactly
    like every major email platform's one-click unsubscribe.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        try:
            subscriber_id = verify_unsubscribe_token(token)
        except signing.SignatureExpired:
            return Response({"detail": "This unsubscribe link has expired."}, status=400)
        except signing.BadSignature:
            return Response({"detail": "Invalid unsubscribe link."}, status=400)

        try:
            subscriber = NewsletterSubscriber.objects.get(id=subscriber_id)
        except NewsletterSubscriber.DoesNotExist:
            return Response({"detail": "Subscriber not found."}, status=404)

        subscriber.is_active = False
        subscriber.unsubscribed_at = timezone.now()
        subscriber.save(update_fields=["is_active", "unsubscribed_at"])
        return Response({"detail": "You have been unsubscribed."})

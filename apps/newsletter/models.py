"""
Newsletter models: subscribers and admin-sent campaigns.
"""

from django.db import models

from apps.core.models import TimestampedModel


class NewsletterSubscriber(TimestampedModel):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email


class NewsletterCampaign(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"

    subject = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="newsletter_campaigns",
    )
    recipient_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject

"""
Internal analytics: business-event tracking to complement Google Analytics.

Google Analytics tracks visitor behavior; this tracks conversions (enquiries,
applications, subscriptions) so conversion-rate reporting can combine both,
per the planned Business Intelligence phase.
"""

from django.db import models

from apps.core.models import TimestampedModel


class BusinessEvent(TimestampedModel):
    class EventType(models.TextChoices):
        CONTACT_SUBMITTED = "contact_submitted", "Contact Submitted"
        QUOTATION_SUBMITTED = "quotation_submitted", "Quotation Submitted"
        APPLICATION_SUBMITTED = "application_submitted", "Application Submitted"
        NEWSLETTER_SUBSCRIBED = "newsletter_subscribed", "Newsletter Subscribed"
        BLOG_VIEWED = "blog_viewed", "Blog Viewed"

    event_type = models.CharField(max_length=50, choices=EventType.choices)
    source_page = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.event_type} @ {self.created_at:%Y-%m-%d %H:%M}"

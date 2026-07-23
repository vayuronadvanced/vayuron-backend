"""
Contact enquiry model — backs the website's general contact form.
"""

from django.db import models
from django.utils import timezone

from apps.core.models import TimestampedModel
from apps.core.validators import phone_regex_validator


class ContactEnquiry(TimestampedModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In Progress"
        CLOSED = "closed", "Closed"

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(
        max_length=20, blank=True, validators=[phone_regex_validator]
    )
    company = models.CharField(max_length=150, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    assigned_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_contact_enquiries",
    )
    internal_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} — {self.subject or 'General Enquiry'}"


class Question(TimestampedModel):
    """
    Public "Ask a Question" submissions from the Contact page.

    Mirrors the blog app's draft/published workflow: a visitor submits a
    question (PENDING), staff answer it and flip it to PUBLISHED via
    publish() — only then does it appear in the public FAQ list.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PUBLISHED = "published", "Published"

    name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    question_text = models.TextField(max_length=2000)

    answer_text = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    published_at = models.DateTimeField(null=True, blank=True)

    def publish(self):
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at"])

    def __str__(self):
        preview = self.question_text[:60]
        return f"{preview}…" if len(self.question_text) > 60 else preview

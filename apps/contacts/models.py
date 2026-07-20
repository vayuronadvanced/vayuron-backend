"""
Contact enquiry model — backs the website's general contact form.
"""

from django.db import models

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

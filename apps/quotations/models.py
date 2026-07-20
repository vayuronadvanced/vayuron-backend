"""
Quotation request model — for product/sector-specific pricing enquiries,
distinct from the general contact form.
"""

from django.db import models

from apps.core.models import TimestampedModel
from apps.core.validators import phone_regex_validator


class QuotationRequest(TimestampedModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        REVIEWED = "reviewed", "Reviewed"
        QUOTED = "quoted", "Quoted"
        CLOSED = "closed", "Closed"

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(
        max_length=20, blank=True, validators=[phone_regex_validator]
    )
    company = models.CharField(max_length=150, blank=True)

    product_or_sector = models.CharField(
        max_length=150,
        blank=True,
        help_text="Product or sector page this quotation request originated from",
    )
    requirements = models.TextField()
    quantity = models.PositiveIntegerField(null=True, blank=True)

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
        related_name="assigned_quotation_requests",
    )
    internal_notes = models.TextField(blank=True)
    quoted_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return f"{self.name} — {self.product_or_sector or 'General'}"

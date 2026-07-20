"""
Careers models: job listings and candidate applications.

Uploaded resume/certificate files are stored on VPS disk under MEDIA_ROOT;
these models store only the file path (via FileField) and metadata.
"""

from django.db import models

from apps.core.models import TimestampedModel
from apps.core.validators import (
    phone_regex_validator,
    validate_certificate_file,
    validate_resume_file,
)


def resume_upload_path(instance, filename):
    return f"uploads/resumes/{filename}"


def certificate_upload_path(instance, filename):
    return f"uploads/certificates/{filename}"


class JobListing(TimestampedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    department = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=150, blank=True)
    employment_type = models.CharField(max_length=50, blank=True)  # e.g. Full-time
    description = models.TextField()
    requirements = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    def __str__(self):
        return self.title


class JobApplication(TimestampedModel):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under Review"
        SHORTLISTED = "shortlisted", "Shortlisted"
        REJECTED = "rejected", "Rejected"
        HIRED = "hired", "Hired"

    job_listing = models.ForeignKey(
        JobListing,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(
        max_length=20, blank=True, validators=[phone_regex_validator]
    )

    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    cover_letter = models.TextField(blank=True)

    resume = models.FileField(
        upload_to=resume_upload_path, validators=validate_resume_file
    )
    certificate = models.FileField(
        upload_to=certificate_upload_path,
        null=True,
        blank=True,
        validators=validate_certificate_file,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )
    internal_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.full_name} — {self.job_listing.title}"

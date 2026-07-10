"""
Generic uploaded-file metadata registry.

Covers standalone files not already tied to a specific model (e.g. brochures,
certification images, misc. documents). The binary lives on VPS disk under
MEDIA_ROOT/uploads/; this table stores only metadata and the path.
"""

from django.db import models

from apps.core.models import TimestampedModel
from apps.core.validators import validate_general_document


def generic_upload_path(instance, filename):
    return f"uploads/documents/{filename}"


class UploadedFile(TimestampedModel):
    class FileType(models.TextChoices):
        PDF = "pdf", "PDF"
        IMAGE = "image", "Image"
        CERTIFICATE = "certificate", "Certificate"
        ZIP = "zip", "ZIP"
        OTHER = "other", "Other"

    file = models.FileField(
        upload_to=generic_upload_path, validators=validate_general_document
    )
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(
        max_length=20,
        choices=FileType.choices,
        default=FileType.OTHER,
    )
    size_bytes = models.PositiveBigIntegerField(null=True, blank=True)
    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
    )
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.original_filename

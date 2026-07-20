"""
Shared validators for Phase 2.5 (Business Logic & Validation).
Import these into model fields or serializer validate_* methods rather than
duplicating regex/size/type checks per app.

Class-based (not closures) so Django can serialize them into migration files.
"""

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible

# --- Phone numbers ---
# Accepts optional leading +, 7-15 digits (loose international format).
phone_regex_validator = RegexValidator(
    regex=r"^\+?\d{7,15}$",
    message="Enter a valid phone number (7–15 digits, optional leading +).",
)


@deconstructible
class MaxFileSizeValidator:
    """Enforces a max file size in megabytes. Deconstructible for migrations."""

    def __init__(self, max_mb):
        self.max_mb = max_mb

    def __call__(self, file):
        limit_bytes = self.max_mb * 1024 * 1024
        if file.size > limit_bytes:
            raise ValidationError(f"File must be {self.max_mb}MB or smaller.")

    def __eq__(self, other):
        return isinstance(other, MaxFileSizeValidator) and self.max_mb == other.max_mb


@deconstructible
class FileExtensionAllowlistValidator:
    """Enforces an allowed file extension whitelist. Deconstructible for migrations."""

    def __init__(self, allowed_extensions):
        self.allowed_extensions = allowed_extensions

    def __call__(self, file):
        name = getattr(file, "name", "") or ""
        ext = name[name.rfind(".") :].lower() if "." in name else ""
        if ext not in self.allowed_extensions:
            allowed = ", ".join(self.allowed_extensions)
            raise ValidationError(f"Unsupported file type. Allowed: {allowed}")

    def __eq__(self, other):
        return (
            isinstance(other, FileExtensionAllowlistValidator)
            and self.allowed_extensions == other.allowed_extensions
        )


# Convenience presets matching the Phase 2.6 storage convention
validate_resume_file = [
    MaxFileSizeValidator(5),
    FileExtensionAllowlistValidator([".pdf", ".doc", ".docx"]),
]

validate_certificate_file = [
    MaxFileSizeValidator(5),
    FileExtensionAllowlistValidator([".pdf", ".jpg", ".jpeg", ".png"]),
]

validate_image_file = [
    MaxFileSizeValidator(3),
    FileExtensionAllowlistValidator([".jpg", ".jpeg", ".png", ".webp"]),
]

validate_general_document = [
    MaxFileSizeValidator(10),
    FileExtensionAllowlistValidator(
        [".pdf", ".doc", ".docx", ".zip", ".jpg", ".jpeg", ".png"]
    ),
]

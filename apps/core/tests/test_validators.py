"""
Tests for apps/core/validators.py — the shared phone/file validators used
across accounts, contacts, quotations, careers, blog, and uploads.
"""

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.validators import (
    FileExtensionAllowlistValidator,
    MaxFileSizeValidator,
    phone_regex_validator,
)


class TestPhoneRegexValidator:
    @pytest.mark.parametrize("phone", ["+919876543210", "9876543210", "+1234567"])
    def test_accepts_valid_phone_numbers(self, phone):
        phone_regex_validator(phone)  # should not raise

    @pytest.mark.parametrize("phone", ["abc123", "123", "+" + "1" * 20, "98-76-54"])
    def test_rejects_invalid_phone_numbers(self, phone):
        with pytest.raises(ValidationError):
            phone_regex_validator(phone)


class TestMaxFileSizeValidator:
    def test_accepts_file_under_limit(self):
        validator = MaxFileSizeValidator(5)
        small_file = SimpleUploadedFile("small.pdf", b"x" * 100)
        validator(small_file)  # should not raise

    def test_rejects_file_over_limit(self):
        validator = MaxFileSizeValidator(1)
        big_file = SimpleUploadedFile("big.pdf", b"x" * (2 * 1024 * 1024))
        with pytest.raises(ValidationError):
            validator(big_file)

    def test_validators_with_same_limit_are_equal(self):
        # Required for Django migrations to correctly detect "no change".
        assert MaxFileSizeValidator(5) == MaxFileSizeValidator(5)
        assert MaxFileSizeValidator(5) != MaxFileSizeValidator(10)


class TestFileExtensionAllowlistValidator:
    def test_accepts_allowed_extension(self):
        validator = FileExtensionAllowlistValidator([".pdf", ".docx"])
        file = SimpleUploadedFile("resume.pdf", b"content")
        validator(file)  # should not raise

    def test_rejects_disallowed_extension(self):
        validator = FileExtensionAllowlistValidator([".pdf", ".docx"])
        file = SimpleUploadedFile("resume.exe", b"content")
        with pytest.raises(ValidationError):
            validator(file)

    def test_case_insensitive(self):
        validator = FileExtensionAllowlistValidator([".pdf"])
        file = SimpleUploadedFile("resume.PDF", b"content")
        validator(file)  # should not raise

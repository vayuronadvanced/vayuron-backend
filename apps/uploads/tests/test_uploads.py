"""
Tests for UploadedFile: staff-only generic file registry.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.uploads.models import UploadedFile

pytestmark = pytest.mark.django_db


class TestStaffAccess:
    def test_anonymous_cannot_upload(self, api_client):
        file = SimpleUploadedFile("doc.pdf", b"x" * 100, content_type="application/pdf")
        response = api_client.post(
            reverse("uploads:uploaded-file-list"), {"file": file}, format="multipart"
        )
        assert response.status_code == 401

    def test_customer_cannot_upload(self, customer_client):
        """Found during Phase 5.4 review: only the anonymous case was tested."""
        file = SimpleUploadedFile("doc.pdf", b"x" * 100, content_type="application/pdf")
        response = customer_client.post(
            reverse("uploads:uploaded-file-list"), {"file": file}, format="multipart"
        )
        assert response.status_code == 403

    def test_staff_upload_autofills_metadata(self, employee_client, employee_user):
        file = SimpleUploadedFile("brochure.pdf", b"x" * 200, content_type="application/pdf")
        response = employee_client.post(
            reverse("uploads:uploaded-file-list"), {"file": file}, format="multipart"
        )
        assert response.status_code == 201
        uploaded = UploadedFile.objects.get(id=response.data["id"])
        assert uploaded.original_filename == "brochure.pdf"
        assert uploaded.size_bytes == 200
        assert uploaded.uploaded_by == employee_user

    def test_oversized_file_rejected(self, employee_client):
        big_file = SimpleUploadedFile(
            "huge.pdf", b"x" * (11 * 1024 * 1024), content_type="application/pdf"
        )
        response = employee_client.post(
            reverse("uploads:uploaded-file-list"), {"file": big_file}, format="multipart"
        )
        assert response.status_code == 400

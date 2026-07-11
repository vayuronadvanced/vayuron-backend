"""
Tests for JobListing/JobApplication: public listing browse, application
submission with resume validation, and the one-active-application-per-
listing dedupe rule (Phase 2.5).
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.careers.models import JobApplication, JobListing

pytestmark = pytest.mark.django_db


@pytest.fixture
def open_listing(db):
    return JobListing.objects.create(
        title="Flight Systems Engineer",
        slug="flight-systems-engineer",
        description="Design and test UAV flight control systems.",
        status=JobListing.Status.OPEN,
    )


def application_payload(listing, resume=None, **overrides):
    payload = {
        "job_listing": listing.id,
        "full_name": "Priya Sharma",
        "email": "priya@example.com",
        "resume": resume or SimpleUploadedFile("resume.pdf", b"x" * 100, content_type="application/pdf"),
    }
    payload.update(overrides)
    return payload


class TestPublicListingBrowse:
    def test_anyone_can_list_open_positions(self, api_client, open_listing):
        response = api_client.get(reverse("careers:job-listing-list"))
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_anyone_can_retrieve_a_listing_by_slug(self, api_client, open_listing):
        url = reverse("careers:job-listing-detail", kwargs={"slug": open_listing.slug})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["title"] == open_listing.title

    def test_anonymous_cannot_create_a_listing(self, api_client):
        response = api_client.post(
            reverse("careers:job-listing-list"),
            {"title": "New Role", "slug": "new-role", "description": "..."},
        )
        assert response.status_code == 401


class TestApplicationSubmission:
    def test_valid_application_is_accepted(self, api_client, open_listing):
        response = api_client.post(
            reverse("careers:job-application-list"),
            application_payload(open_listing),
            format="multipart",
        )
        assert response.status_code == 201
        assert JobApplication.objects.count() == 1

    def test_oversized_resume_rejected(self, api_client, open_listing):
        big_resume = SimpleUploadedFile(
            "resume.pdf", b"x" * (6 * 1024 * 1024), content_type="application/pdf"
        )
        response = api_client.post(
            reverse("careers:job-application-list"),
            application_payload(open_listing, resume=big_resume),
            format="multipart",
        )
        assert response.status_code == 400

    def test_disallowed_resume_extension_rejected(self, api_client, open_listing):
        bad_resume = SimpleUploadedFile("resume.exe", b"x" * 100, content_type="application/octet-stream")
        response = api_client.post(
            reverse("careers:job-application-list"),
            application_payload(open_listing, resume=bad_resume),
            format="multipart",
        )
        assert response.status_code == 400

    def test_duplicate_active_application_rejected(self, api_client, open_listing):
        payload = application_payload(open_listing)
        first = api_client.post(reverse("careers:job-application-list"), payload, format="multipart")
        assert first.status_code == 201

        second_payload = application_payload(
            open_listing,
            resume=SimpleUploadedFile("resume2.pdf", b"y" * 50, content_type="application/pdf"),
        )
        second = api_client.post(reverse("careers:job-application-list"), second_payload, format="multipart")
        assert second.status_code == 400

    def test_reapplication_allowed_after_rejection(self, api_client, open_listing):
        payload = application_payload(open_listing)
        first_response = api_client.post(reverse("careers:job-application-list"), payload, format="multipart")
        application = JobApplication.objects.get(id=first_response.data["id"])
        application.status = JobApplication.Status.REJECTED
        application.save()

        second_payload = application_payload(
            open_listing,
            resume=SimpleUploadedFile("resume2.pdf", b"z" * 50, content_type="application/pdf"),
        )
        second = api_client.post(reverse("careers:job-application-list"), second_payload, format="multipart")
        assert second.status_code == 201


class TestStaffAccess:
    def test_anonymous_cannot_list_applications(self, api_client):
        response = api_client.get(reverse("careers:job-application-list"))
        assert response.status_code == 401

    def test_staff_can_update_application_status(self, employee_client, open_listing):
        application = JobApplication.objects.create(
            job_listing=open_listing,
            full_name="Test Candidate",
            email="test@example.com",
            resume=SimpleUploadedFile("r.pdf", b"x" * 50, content_type="application/pdf"),
        )
        url = reverse("careers:job-application-detail", kwargs={"pk": application.id})
        response = employee_client.patch(url, {"status": "shortlisted"})
        assert response.status_code == 200
        application.refresh_from_db()
        assert application.status == "shortlisted"

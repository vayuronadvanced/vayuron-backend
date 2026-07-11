"""
Tests for ContactEnquiry: public submission, duplicate-submission dedupe
rule (Phase 2.5), and staff-only list/management (Phase 4.1/4.3).
"""

import pytest
from django.urls import reverse

from apps.contacts.models import ContactEnquiry

pytestmark = pytest.mark.django_db


def enquiry_payload(**overrides):
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "message": "Interested in your UAV systems.",
    }
    payload.update(overrides)
    return payload


class TestPublicSubmission:
    def test_anyone_can_submit_an_enquiry(self, api_client):
        response = api_client.post(reverse("contacts:contact-enquiry-list"), enquiry_payload())
        assert response.status_code == 201
        assert ContactEnquiry.objects.count() == 1

    def test_duplicate_submission_within_window_is_rejected(self, api_client):
        payload = enquiry_payload()
        first = api_client.post(reverse("contacts:contact-enquiry-list"), payload)
        assert first.status_code == 201

        second = api_client.post(reverse("contacts:contact-enquiry-list"), payload)
        assert second.status_code == 400

    def test_different_message_is_not_treated_as_duplicate(self, api_client):
        api_client.post(reverse("contacts:contact-enquiry-list"), enquiry_payload(message="First message"))
        response = api_client.post(
            reverse("contacts:contact-enquiry-list"), enquiry_payload(message="A completely different message")
        )
        assert response.status_code == 201

    def test_invalid_phone_number_rejected(self, api_client):
        response = api_client.post(
            reverse("contacts:contact-enquiry-list"), enquiry_payload(phone_number="not-a-phone")
        )
        assert response.status_code == 400


class TestStaffAccess:
    def test_anonymous_cannot_list_enquiries(self, api_client):
        response = api_client.get(reverse("contacts:contact-enquiry-list"))
        assert response.status_code == 401

    def test_customer_cannot_list_enquiries(self, customer_client):
        response = customer_client.get(reverse("contacts:contact-enquiry-list"))
        assert response.status_code == 403

    def test_staff_can_list_and_update_enquiries(self, employee_client):
        enquiry = ContactEnquiry.objects.create(**enquiry_payload())

        list_response = employee_client.get(reverse("contacts:contact-enquiry-list"))
        assert list_response.status_code == 200

        detail_url = reverse("contacts:contact-enquiry-detail", kwargs={"pk": enquiry.id})
        update_response = employee_client.patch(detail_url, {"status": "in_progress"})
        assert update_response.status_code == 200
        enquiry.refresh_from_db()
        assert enquiry.status == "in_progress"

    def test_search_filters_results(self, employee_client):
        ContactEnquiry.objects.create(**enquiry_payload(name="Alice", message="About drones"))
        ContactEnquiry.objects.create(**enquiry_payload(email="bob@example.com", message="About pricing"))

        response = employee_client.get(reverse("contacts:contact-enquiry-list"), {"search": "drones"})
        assert response.status_code == 200
        assert response.data["count"] == 1

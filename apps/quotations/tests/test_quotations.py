"""
Tests for QuotationRequest: public submission and staff-only management.
"""

import pytest
from django.urls import reverse

from apps.quotations.models import QuotationRequest

pytestmark = pytest.mark.django_db


def quotation_payload(**overrides):
    payload = {
        "name": "Rahul Mehta",
        "email": "rahul@example.com",
        "product_or_sector": "UAV Systems",
        "requirements": "Need 5 units for agricultural survey.",
    }
    payload.update(overrides)
    return payload


class TestPublicSubmission:
    def test_anyone_can_submit_a_quotation_request(self, api_client):
        response = api_client.post(reverse("quotations:quotation-request-list"), quotation_payload())
        assert response.status_code == 201
        assert QuotationRequest.objects.count() == 1

    def test_missing_requirements_rejected(self, api_client):
        payload = quotation_payload()
        del payload["requirements"]
        response = api_client.post(reverse("quotations:quotation-request-list"), payload)
        assert response.status_code == 400


class TestStaffAccess:
    def test_anonymous_cannot_list(self, api_client):
        response = api_client.get(reverse("quotations:quotation-request-list"))
        assert response.status_code == 401

    def test_staff_can_update_status_and_quoted_amount(self, employee_client):
        quotation = QuotationRequest.objects.create(**quotation_payload())
        url = reverse("quotations:quotation-request-detail", kwargs={"pk": quotation.id})
        response = employee_client.patch(url, {"status": "quoted", "quoted_amount": "150000.00"})
        assert response.status_code == 200
        quotation.refresh_from_db()
        assert quotation.status == "quoted"
        assert str(quotation.quoted_amount) == "150000.00"

    def test_filter_by_status(self, employee_client):
        QuotationRequest.objects.create(**quotation_payload(status="closed"))
        QuotationRequest.objects.create(**quotation_payload(email="other@example.com"))

        response = employee_client.get(reverse("quotations:quotation-request-list"), {"status": "closed"})
        assert response.status_code == 200
        assert response.data["count"] == 1

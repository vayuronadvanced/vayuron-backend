"""
Tests for BusinessEvent: public event logging, staff-only read (Phase 7.2 prep).
"""

import pytest
from django.urls import reverse

from apps.analytics.models import BusinessEvent

pytestmark = pytest.mark.django_db


class TestEventLogging:
    def test_anyone_can_log_an_event(self, api_client):
        response = api_client.post(
            reverse("analytics:business-event-list"),
            {"event_type": "contact_submitted", "source_page": "/contact"},
        )
        assert response.status_code == 201
        assert BusinessEvent.objects.count() == 1

    def test_metadata_field_accepts_arbitrary_json(self, api_client):
        response = api_client.post(
            reverse("analytics:business-event-list"),
            {
                "event_type": "blog_viewed",
                "source_page": "/blog/my-post",
                "metadata": {"post_slug": "my-post", "referrer": "google"},
            },
            format="json",
        )
        assert response.status_code == 201
        event = BusinessEvent.objects.get(id=response.data["id"])
        assert event.metadata["post_slug"] == "my-post"


class TestStaffAccess:
    def test_anonymous_cannot_list_events(self, api_client):
        response = api_client.get(reverse("analytics:business-event-list"))
        assert response.status_code == 401

    def test_staff_can_filter_by_event_type(self, employee_client):
        BusinessEvent.objects.create(event_type="contact_submitted", source_page="/contact")
        BusinessEvent.objects.create(event_type="blog_viewed", source_page="/blog/post")

        response = employee_client.get(
            reverse("analytics:business-event-list"), {"event_type": "contact_submitted"}
        )
        assert response.status_code == 200
        assert response.data["count"] == 1

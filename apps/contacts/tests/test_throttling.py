"""
Explicit test that the public_submission throttle (Phase 2.5, 10/hour)
actually engages — kept separate from test_contacts.py since it
deliberately does NOT rely on the clear_throttle_cache autouse fixture
resetting between individual requests within the same test.
"""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_exceeding_public_submission_rate_limit_returns_429(api_client):
    url = reverse("contacts:contact-enquiry-list")
    payload = {"name": "Spammer", "email": "spam@example.com", "message": "msg"}

    responses = []
    for i in range(11):
        # Vary the message each time so the duplicate-submission dedupe rule
        # (Phase 2.5) doesn't mask the throttle behavior we're testing here.
        responses.append(
            api_client.post(url, {**payload, "message": f"msg {i}"})
        )

    statuses = [r.status_code for r in responses]
    assert statuses[:10] == [201] * 10
    assert statuses[10] == 429

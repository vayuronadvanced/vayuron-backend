"""
Tests for the /api/core/health/ endpoint — used by nginx/uptime monitors
and referenced in monitoring/health-checks/.
"""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def test_health_check_returns_200_when_database_is_reachable(api_client):
    url = reverse("core:health")
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data == {"status": "ok", "database": "ok"}


def test_health_check_does_not_require_authentication(api_client):
    # No credentials/auth headers set on api_client here — an unauthenticated
    # request must still succeed, since external monitors won't have a login.
    url = reverse("core:health")
    response = api_client.get(url)

    assert response.status_code != 401
    assert response.status_code != 403

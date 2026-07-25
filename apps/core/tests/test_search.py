"""
Tests for GET /api/search/ — the unified full-text search endpoint over
published BlogPost and open JobListing rows.

Self-contained (defines its own fixtures rather than relying on a shared
conftest) to match the working pattern in test_health.py — some other test
modules in this repo (e.g. apps/blog/tests/test_blog.py) reference
employee_user/employee_client fixtures that aren't defined anywhere in the
project, which would error if run; this file avoids that by not depending
on them.
"""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.blog.models import BlogPost
from apps.careers.models import JobListing

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def published_post(db):
    return BlogPost.objects.create(
        title="Autonomous Drone Navigation",
        slug="autonomous-drone-navigation",
        excerpt="How VAYURON approaches GPS-denied navigation.",
        content="Deep dive into inertial and visual navigation for UAV platforms.",
        status=BlogPost.Status.PUBLISHED,
    )


@pytest.fixture
def draft_post(db):
    return BlogPost.objects.create(
        title="Unreleased Drone Roadmap",
        slug="unreleased-drone-roadmap",
        content="Internal roadmap notes about upcoming drone platforms.",
        status=BlogPost.Status.DRAFT,
    )


@pytest.fixture
def open_listing(db):
    return JobListing.objects.create(
        title="Autonomy Software Engineer",
        slug="autonomy-software-engineer",
        description="Build navigation and autonomy stacks for UAV platforms.",
        status=JobListing.Status.OPEN,
    )


@pytest.fixture
def closed_listing(db):
    return JobListing.objects.create(
        title="Autonomy Intern (Closed)",
        slug="autonomy-intern-closed",
        description="This role for autonomy work is no longer open.",
        status=JobListing.Status.CLOSED,
    )


def _search(api_client, query):
    url = reverse("search:global-search")
    return api_client.get(url, {"q": query})


class TestVisibility:
    def test_published_post_is_returned(self, api_client, published_post):
        response = _search(api_client, "drone navigation")
        assert response.status_code == 200
        titles = [r["title"] for r in response.data["results"]]
        assert "Autonomous Drone Navigation" in titles

    def test_draft_post_is_never_returned(self, api_client, draft_post):
        response = _search(api_client, "drone roadmap")
        assert response.status_code == 200
        titles = [r["title"] for r in response.data["results"]]
        assert "Unreleased Drone Roadmap" not in titles

    def test_open_listing_is_returned(self, api_client, open_listing):
        response = _search(api_client, "autonomy software engineer")
        assert response.status_code == 200
        titles = [r["title"] for r in response.data["results"]]
        assert "Autonomy Software Engineer" in titles

    def test_closed_listing_is_never_returned(self, api_client, closed_listing):
        response = _search(api_client, "autonomy intern")
        assert response.status_code == 200
        titles = [r["title"] for r in response.data["results"]]
        assert "Autonomy Intern (Closed)" not in titles

    def test_search_does_not_require_authentication(self, api_client, published_post):
        response = _search(api_client, "drone")
        assert response.status_code != 401
        assert response.status_code != 403


class TestResultShape:
    def test_result_has_normalized_shape(self, api_client, published_post):
        response = _search(api_client, "drone navigation")
        result = response.data["results"][0]
        assert set(result.keys()) == {"type", "title", "snippet", "url", "score"}
        assert result["type"] == "blog"
        assert result["url"] == "/blog/autonomous-drone-navigation"

    def test_job_listing_result_has_careers_type_and_url(self, api_client, open_listing):
        response = _search(api_client, "autonomy engineer")
        result = response.data["results"][0]
        assert result["type"] == "careers"
        assert result["url"] == "/careers/autonomy-software-engineer"

    def test_results_combine_and_sort_across_types_by_score(
        self, api_client, published_post, open_listing
    ):
        response = _search(api_client, "autonomy drone navigation uav")
        types = {r["type"] for r in response.data["results"]}
        assert types == {"blog", "careers"}
        scores = [r["score"] for r in response.data["results"]]
        assert scores == sorted(scores, reverse=True)


class TestEdgeCases:
    def test_empty_query_returns_no_results_without_error(self, api_client):
        response = _search(api_client, "")
        assert response.status_code == 200
        assert response.data["results"] == []

    def test_query_below_minimum_length_returns_no_results(self, api_client, published_post):
        response = _search(api_client, "d")
        assert response.status_code == 200
        assert response.data["results"] == []

    def test_no_matches_returns_empty_list_not_error(self, api_client, published_post):
        response = _search(api_client, "zzz_no_such_term_zzz")
        assert response.status_code == 200
        assert response.data["results"] == []

    def test_missing_query_param_does_not_error(self, api_client):
        response = api_client.get(reverse("search:global-search"))
        assert response.status_code == 200
        assert response.data["results"] == []

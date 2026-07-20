"""
Tests for BlogPost/BlogCategory: public visitors only see published posts,
staff see everything including drafts, and the publish action (Phase 4.2).
"""

import pytest
from django.urls import reverse

from apps.blog.models import BlogPost

pytestmark = pytest.mark.django_db


@pytest.fixture
def draft_post(db, employee_user):
    return BlogPost.objects.create(
        title="Draft Post",
        slug="draft-post",
        content="<p>Not yet public.</p>",
        status=BlogPost.Status.DRAFT,
        author=employee_user,
    )


@pytest.fixture
def published_post(db, employee_user):
    return BlogPost.objects.create(
        title="Published Post",
        slug="published-post",
        content="<p>Public content.</p>",
        status=BlogPost.Status.PUBLISHED,
        author=employee_user,
    )


class TestPublicVisibility:
    def test_anonymous_sees_only_published_posts(self, api_client, draft_post, published_post):
        response = api_client.get(reverse("blog:blog-post-list"))
        assert response.status_code == 200
        titles = [p["title"] for p in response.data["results"]]
        assert "Published Post" in titles
        assert "Draft Post" not in titles

    def test_anonymous_cannot_retrieve_draft_by_slug(self, api_client, draft_post):
        url = reverse("blog:blog-post-detail", kwargs={"slug": draft_post.slug})
        response = api_client.get(url)
        assert response.status_code == 404

    def test_anonymous_can_retrieve_published_post(self, api_client, published_post):
        url = reverse("blog:blog-post-detail", kwargs={"slug": published_post.slug})
        response = api_client.get(url)
        assert response.status_code == 200


class TestStaffVisibility:
    def test_staff_sees_drafts_too(self, employee_client, draft_post, published_post):
        response = employee_client.get(reverse("blog:blog-post-list"))
        assert response.status_code == 200
        assert response.data["count"] == 2


class TestCategoryPermissions:
    """
    Coverage gap found during Phase 5.4 security review: category
    read-permissions were exercised indirectly, but write-permissions
    (create/update/delete) had no explicit test.
    """

    def test_anonymous_cannot_create_category(self, api_client):
        response = api_client.post(
            reverse("blog:blog-category-list"), {"name": "Hacked", "slug": "hacked"}
        )
        assert response.status_code == 401

    def test_customer_cannot_create_category(self, customer_client):
        response = customer_client.post(
            reverse("blog:blog-category-list"), {"name": "Hacked", "slug": "hacked"}
        )
        assert response.status_code == 403

    def test_staff_can_create_category(self, employee_client):
        response = employee_client.post(
            reverse("blog:blog-category-list"), {"name": "Engineering", "slug": "engineering"}
        )
        assert response.status_code == 201

    def test_anyone_can_list_categories(self, api_client):
        response = api_client.get(reverse("blog:blog-category-list"))
        assert response.status_code == 200


class TestPublishAction:
    def test_staff_can_publish_a_draft(self, employee_client, draft_post):
        url = reverse("blog:blog-post-publish", kwargs={"slug": draft_post.slug})
        response = employee_client.post(url)
        assert response.status_code == 200
        draft_post.refresh_from_db()
        assert draft_post.status == BlogPost.Status.PUBLISHED
        assert draft_post.published_at is not None

    def test_anonymous_cannot_publish(self, api_client, draft_post):
        url = reverse("blog:blog-post-publish", kwargs={"slug": draft_post.slug})
        response = api_client.post(url)
        # IsAdminOrEmployee is checked before object lookup, so this is a
        # straightforward auth rejection rather than a 404.
        assert response.status_code == 401

    def test_created_post_is_attributed_to_author(self, employee_client, employee_user):
        response = employee_client.post(
            reverse("blog:blog-post-list"),
            {"title": "New Post", "slug": "new-post", "content": "<p>Hello</p>"},
        )
        assert response.status_code == 201
        assert response.data["author"] == employee_user.id

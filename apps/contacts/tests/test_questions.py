"""
Tests for Question ("Ask a Question" on the Contact page): public
submission, published-only visibility for anonymous visitors, and
staff-only edit/answer/publish — mirroring the blog app's draft/published
workflow (see apps/blog/tests/test_blog.py).
"""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.contacts.models import Question

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def staff_api_client(db):
    staff = User.objects.create_user(
        username="staff_member", email="staff@vayuron.com", password="pass12345", role="admin"
    )
    client = APIClient()
    client.force_authenticate(user=staff)
    return client


def question_payload(**overrides):
    payload = {
        "name": "Rahul Verma",
        "email": "rahul@example.com",
        "question_text": "What is the max flight time of the UAV?",
    }
    payload.update(overrides)
    return payload


class TestPublicSubmission:
    def test_anyone_can_submit_a_question(self, api_client):
        response = api_client.post(reverse("contacts:question-list"), question_payload())
        assert response.status_code == 201
        assert Question.objects.count() == 1
        assert Question.objects.first().status == Question.Status.PENDING

    def test_duplicate_submission_within_window_is_rejected(self, api_client):
        payload = question_payload()
        first = api_client.post(reverse("contacts:question-list"), payload)
        assert first.status_code == 201

        second = api_client.post(reverse("contacts:question-list"), payload)
        assert second.status_code == 400

    def test_submit_response_never_exposes_answer_fields(self, api_client):
        response = api_client.post(reverse("contacts:question-list"), question_payload())
        assert "answer_text" not in response.data
        assert "status" not in response.data


class TestPublicVisibility:
    def test_pending_question_is_not_listed_publicly(self, api_client):
        Question.objects.create(**question_payload())
        response = api_client.get(reverse("contacts:question-list"))
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 0

    def test_published_question_is_listed_publicly_with_its_answer(self, api_client):
        question = Question.objects.create(
            **question_payload(), answer_text="Up to 90 minutes depending on payload."
        )
        question.publish()

        response = api_client.get(reverse("contacts:question-list"))
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["question_text"] == question.question_text
        assert results[0]["answer_text"] == question.answer_text
        # Public serializer must not leak the asker's contact details.
        assert "email" not in results[0]
        assert "name" not in results[0]


class TestStaffManagement:
    def test_anonymous_user_cannot_edit_a_question(self, api_client):
        question = Question.objects.create(**question_payload())
        response = api_client.patch(
            reverse("contacts:question-detail", args=[question.id]),
            {"answer_text": "hacked"},
        )
        assert response.status_code in (401, 403)

    def test_staff_can_answer_and_publish_a_question(self, staff_api_client):
        question = Question.objects.create(**question_payload())

        answer_response = staff_api_client.patch(
            reverse("contacts:question-detail", args=[question.id]),
            {"answer_text": "Up to 90 minutes depending on payload."},
        )
        assert answer_response.status_code == 200

        publish_response = staff_api_client.post(
            reverse("contacts:question-publish", args=[question.id])
        )
        assert publish_response.status_code == 200

        question.refresh_from_db()
        assert question.status == Question.Status.PUBLISHED
        assert question.published_at is not None

    def test_staff_list_includes_pending_questions(self, staff_api_client):
        Question.objects.create(**question_payload())
        response = staff_api_client.get(reverse("contacts:question-list"))
        results = response.data.get("results", response.data)
        assert len(results) == 1

"""
Tests for NewsletterSubscriber/NewsletterCampaign: the reactivate-on-
resubscribe business rule (Phase 2.5), and campaign send (Phase 4.1).
"""

import pytest
from django.urls import reverse

from apps.newsletter.models import NewsletterCampaign, NewsletterSubscriber
from apps.newsletter.utils import generate_unsubscribe_token

pytestmark = pytest.mark.django_db


class TestSubscription:
    def test_anyone_can_subscribe(self, api_client):
        response = api_client.post(
            reverse("newsletter:newsletter-subscriber-list"), {"email": "new@example.com"}
        )
        assert response.status_code == 201
        assert NewsletterSubscriber.objects.get(email="new@example.com").is_active

    def test_subscribing_twice_while_active_is_rejected(self, api_client):
        api_client.post(reverse("newsletter:newsletter-subscriber-list"), {"email": "dup@example.com"})
        response = api_client.post(
            reverse("newsletter:newsletter-subscriber-list"), {"email": "dup@example.com"}
        )
        assert response.status_code == 400

    def test_resubscribing_after_unsubscribe_reactivates(self, api_client):
        subscriber = NewsletterSubscriber.objects.create(email="back@example.com", is_active=False)
        response = api_client.post(
            reverse("newsletter:newsletter-subscriber-list"), {"email": "back@example.com"}
        )
        assert response.status_code == 201
        subscriber.refresh_from_db()
        assert subscriber.is_active is True
        # Reactivation reuses the existing row rather than creating a duplicate.
        assert NewsletterSubscriber.objects.filter(email="back@example.com").count() == 1


class TestStaffAccess:
    def test_anonymous_cannot_list_subscribers(self, api_client):
        response = api_client.get(reverse("newsletter:newsletter-subscriber-list"))
        assert response.status_code == 401

    def test_staff_can_filter_active_subscribers(self, employee_client):
        NewsletterSubscriber.objects.create(email="active@example.com", is_active=True)
        NewsletterSubscriber.objects.create(email="inactive@example.com", is_active=False)

        response = employee_client.get(
            reverse("newsletter:newsletter-subscriber-list"), {"is_active": "true"}
        )
        assert response.status_code == 200
        assert response.data["count"] == 1


class TestCampaignSend:
    def test_send_marks_campaign_sent_and_stamps_recipient_count(self, employee_client, employee_user):
        NewsletterSubscriber.objects.create(email="a@example.com", is_active=True)
        NewsletterSubscriber.objects.create(email="b@example.com", is_active=True)
        NewsletterSubscriber.objects.create(email="c@example.com", is_active=False)

        campaign = NewsletterCampaign.objects.create(subject="Launch", body="...")
        url = reverse("newsletter:newsletter-campaign-send", kwargs={"pk": campaign.id})
        response = employee_client.post(url)

        assert response.status_code == 200
        campaign.refresh_from_db()
        assert campaign.status == NewsletterCampaign.Status.SENT
        assert campaign.recipient_count == 2  # only active subscribers counted
        assert campaign.sent_at is not None

    def test_send_actually_dispatches_real_emails(self, employee_client, mailoutbox):
        """
        Uses Django's locmem email backend (configured in settings.testing)
        which captures sent emails in `mailoutbox` instead of a real SMTP
        connection — lets us assert on actual dispatched content, not just
        the campaign record's bookkeeping fields.
        """
        NewsletterSubscriber.objects.create(email="alice@example.com", is_active=True)
        NewsletterSubscriber.objects.create(email="bob@example.com", is_active=True)

        campaign = NewsletterCampaign.objects.create(subject="Big News", body="Here's what's new.")
        url = reverse("newsletter:newsletter-campaign-send", kwargs={"pk": campaign.id})
        employee_client.post(url)

        assert len(mailoutbox) == 2
        recipients = {email.to[0] for email in mailoutbox}
        assert recipients == {"alice@example.com", "bob@example.com"}
        for email in mailoutbox:
            assert email.subject == "Big News"
            assert "Here's what's new." in email.body
            assert "unsubscribe/" in email.body.lower()
            # One email per recipient, never BCC-everyone-together.
            assert len(email.to) == 1

    def test_cannot_send_the_same_campaign_twice(self, employee_client):
        NewsletterSubscriber.objects.create(email="a@example.com", is_active=True)
        campaign = NewsletterCampaign.objects.create(subject="Launch", body="...")
        url = reverse("newsletter:newsletter-campaign-send", kwargs={"pk": campaign.id})

        first = employee_client.post(url)
        assert first.status_code == 200

        second = employee_client.post(url)
        assert second.status_code == 400

    def test_anonymous_cannot_send_campaign(self, api_client):
        campaign = NewsletterCampaign.objects.create(subject="Launch", body="...")
        url = reverse("newsletter:newsletter-campaign-send", kwargs={"pk": campaign.id})
        response = api_client.post(url)
        assert response.status_code == 401

    def test_customer_cannot_send_campaign(self, customer_client):
        """Found during Phase 5.4 review: only the anonymous case was tested."""
        campaign = NewsletterCampaign.objects.create(subject="Launch", body="...")
        url = reverse("newsletter:newsletter-campaign-send", kwargs={"pk": campaign.id})
        response = customer_client.post(url)
        assert response.status_code == 403


class TestUnsubscribe:
    def test_valid_token_unsubscribes(self, api_client):
        subscriber = NewsletterSubscriber.objects.create(email="leaving@example.com", is_active=True)
        token = generate_unsubscribe_token(subscriber.id)

        url = reverse("newsletter:unsubscribe", kwargs={"token": token})
        response = api_client.post(url)

        assert response.status_code == 200
        subscriber.refresh_from_db()
        assert subscriber.is_active is False
        assert subscriber.unsubscribed_at is not None

    def test_invalid_token_rejected(self, api_client):
        url = reverse("newsletter:unsubscribe", kwargs={"token": "not-a-real-token"})
        response = api_client.post(url)
        assert response.status_code == 400

    def test_unsubscribe_requires_no_authentication(self, api_client):
        """Must work for a logged-out email recipient clicking a link cold."""
        subscriber = NewsletterSubscriber.objects.create(email="anon@example.com", is_active=True)
        token = generate_unsubscribe_token(subscriber.id)
        url = reverse("newsletter:unsubscribe", kwargs={"token": token})
        response = api_client.post(url)
        assert response.status_code == 200

"""
Tests for registration, JWT login, self-service /me/, and admin-only user
management (Phase 4.1).
"""

import pytest
from django.urls import reverse

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


class TestRegistration:
    def test_register_creates_customer_role_account(self, api_client):
        url = reverse("accounts:register")
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "SuperSecret123!",
            "password_confirm": "SuperSecret123!",
        }
        response = api_client.post(url, payload)
        assert response.status_code == 201
        user = User.objects.get(username="newuser")
        assert user.role == User.Role.CUSTOMER
        assert user.check_password("SuperSecret123!")

    def test_register_rejects_mismatched_passwords(self, api_client):
        url = reverse("accounts:register")
        payload = {
            "username": "newuser2",
            "email": "new2@example.com",
            "password": "SuperSecret123!",
            "password_confirm": "DifferentPassword!",
        }
        response = api_client.post(url, payload)
        assert response.status_code == 400

    def test_register_cannot_set_role(self, api_client):
        """A malicious client can't smuggle role=admin into registration."""
        url = reverse("accounts:register")
        payload = {
            "username": "sneaky",
            "email": "sneaky@example.com",
            "password": "SuperSecret123!",
            "password_confirm": "SuperSecret123!",
            "role": "admin",
        }
        response = api_client.post(url, payload)
        assert response.status_code == 201
        user = User.objects.get(username="sneaky")
        assert user.role == User.Role.CUSTOMER


class TestLogin:
    def test_login_returns_access_and_refresh_tokens(self, api_client):
        User.objects.create_user(username="loginuser", password="pass1234")
        url = reverse("accounts:token_obtain_pair")
        response = api_client.post(url, {"username": "loginuser", "password": "pass1234"})
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_rejects_wrong_password(self, api_client):
        User.objects.create_user(username="loginuser2", password="pass1234")
        url = reverse("accounts:token_obtain_pair")
        response = api_client.post(url, {"username": "loginuser2", "password": "wrong"})
        assert response.status_code == 401


class TestMeEndpoint:
    def test_me_requires_authentication(self, api_client):
        response = api_client.get(reverse("accounts:me"))
        assert response.status_code == 401

    def test_me_returns_current_user(self, customer_client, customer_user):
        response = customer_client.get(reverse("accounts:me"))
        assert response.status_code == 200
        assert response.data["username"] == customer_user.username

    def test_me_cannot_change_own_role(self, customer_client, customer_user):
        response = customer_client.patch(reverse("accounts:me"), {"role": "admin"})
        assert response.status_code == 200
        customer_user.refresh_from_db()
        assert customer_user.role == User.Role.CUSTOMER


class TestUserManagement:
    """Admin-only user list/role management (Phase 4.1.3)."""

    def test_anonymous_cannot_list_users(self, api_client):
        response = api_client.get(reverse("accounts:user-list"))
        assert response.status_code == 401

    def test_customer_cannot_list_users(self, customer_client):
        response = customer_client.get(reverse("accounts:user-list"))
        assert response.status_code == 403

    def test_admin_can_list_users(self, admin_client, admin_user):
        response = admin_client.get(reverse("accounts:user-list"))
        assert response.status_code == 200

    def test_admin_can_promote_user_role(self, admin_client, customer_user):
        url = reverse("accounts:user-detail", kwargs={"pk": customer_user.id})
        response = admin_client.patch(url, {"role": "employee"})
        assert response.status_code == 200
        customer_user.refresh_from_db()
        assert customer_user.role == User.Role.EMPLOYEE

    def test_employee_cannot_promote_users(self, employee_client, customer_user):
        url = reverse("accounts:user-detail", kwargs={"pk": customer_user.id})
        response = employee_client.patch(url, {"role": "admin"})
        assert response.status_code == 403

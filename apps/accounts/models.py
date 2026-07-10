"""
Custom user model for the VAYURON backend.

Supports three roles: Admin, Employee, Customer. Using a custom user model
from the start (rather than Django's default) avoids a painful mid-project
migration later, per Django's own recommendation.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.validators import phone_regex_validator


class User(AbstractUser):
    """
    Extends Django's built-in user with a role field.
    Username/email/password/first_name/last_name are inherited from AbstractUser.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        EMPLOYEE = "employee", "Employee"
        CUSTOMER = "customer", "Customer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    phone_number = models.CharField(
        max_length=20, blank=True, validators=[phone_regex_validator]
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

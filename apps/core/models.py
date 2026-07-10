"""
Shared abstract base models for the VAYURON backend.

Other apps' models should inherit from TimestampedModel instead of
redeclaring created_at/updated_at on every table.
"""

from django.db import models


class TimestampedModel(models.Model):
    """
    Abstract base providing created_at / updated_at on every subclass.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

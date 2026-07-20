"""
Testing settings for the VAYURON backend.
Used by pytest-django / CI (DJANGO_SETTINGS_MODULE=config.settings.testing).
"""

from .base import *  # noqa: F401,F403

DEBUG = False

# Fast password hasher — do not use in production.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Throwaway in-memory-style test database (still PostgreSQL under the hood;
# Django creates/destroys a test_<name> database automatically).
DATABASES["default"]["NAME"] = "test_vayuron_db"  # noqa: F405

# Disable outbound email during tests.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Speed up tests: no need for whitenoise/staticfiles collection.
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

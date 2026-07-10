"""
Production settings for the VAYURON backend.
Used on the Hostinger VPS KVM 2 deployment (DJANGO_SETTINGS_MODULE=config.settings.production).
"""

from .base import *  # noqa: F401,F403
from .base import env, BASE_DIR

DEBUG = False

ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=[],
)

# --- Security hardening ---
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# --- Static & media (served by Nginx in production) ---
STATIC_ROOT = env("STATIC_ROOT", default=str(BASE_DIR / "staticfiles"))
MEDIA_ROOT = env("MEDIA_ROOT", default=str(BASE_DIR / "media"))

# --- Logging ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": str(BASE_DIR / "logs" / "django.log"),
        },
    },
    "root": {
        "handlers": ["file"],
        "level": "INFO",
    },
}

# NOTE: Error tracking (e.g. Sentry) to be wired in here once adopted:
#   import sentry_sdk
#   sentry_sdk.init(dsn=env("SENTRY_DSN", default=""))

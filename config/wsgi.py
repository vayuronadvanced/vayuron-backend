"""
WSGI config for the VAYURON backend project.

Exposes the WSGI callable as a module-level variable named ``application``,
used by both `manage.py runserver` and Gunicorn in production.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

application = get_wsgi_application()

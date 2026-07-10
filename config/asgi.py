"""
ASGI config for the VAYURON backend project.

Exposes the ASGI callable as a module-level variable named ``application``.
Reserved for future async/WebSocket use (e.g. Django Channels); not required
for the current synchronous DRF API.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

application = get_asgi_application()

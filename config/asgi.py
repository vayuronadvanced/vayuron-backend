"""
ASGI config for the VAYURON backend project.

Exposes the ASGI callable as a module-level variable named ``application``.
Reserved for future async/WebSocket use (e.g. Django Channels); not required
for the current synchronous DRF API.

Deliberately does NOT default DJANGO_SETTINGS_MODULE here — see the detailed
comment in config/wsgi.py explaining why silently defaulting to development
settings here would be unsafe if this is ever used as a production entrypoint.
"""

from django.core.asgi import get_asgi_application

application = get_asgi_application()

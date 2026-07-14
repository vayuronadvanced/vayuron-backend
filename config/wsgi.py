"""
WSGI config for the VAYURON backend project.

Exposes the WSGI callable as a module-level variable named ``application``,
used by Gunicorn in production (and optionally by `manage.py runserver`,
though manage.py sets its own development default for local convenience).

Deliberately does NOT default DJANGO_SETTINGS_MODULE here. A previous
version used os.environ.setdefault(..., "config.settings.development"),
which — because this line runs before base.py's env.read_env() ever loads
.env — meant Gunicorn could silently boot with development settings
(DEBUG=True, no HSTS, no SSL redirect) in production if the real process
environment didn't already have DJANGO_SETTINGS_MODULE set, even though
.env said otherwise (django-environ's read_env() never overrides an
already-set os.environ variable). Failing loudly here is much safer than
guessing wrong in production. Set DJANGO_SETTINGS_MODULE explicitly in the
systemd unit's Environment= directive (see deployment/gunicorn/).
"""

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

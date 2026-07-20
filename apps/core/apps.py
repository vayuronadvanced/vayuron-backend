from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        # Fixes Django admin's "View site" link, which defaults to "/" on
        # this same Django host — a route that doesn't exist here since the
        # frontend is a separate React SPA. Point it at the real frontend.
        from django.conf import settings
        from django.contrib import admin

        admin.site.site_url = settings.FRONTEND_URL

"""
URL routes for the 'core' app.
Empty router for now — endpoints will be registered here as views/serializers
for this app are implemented in a later phase. Kept non-empty (urlpatterns = [])
so config/urls.py's include("apps.core.urls") resolves without error.
"""

from django.urls import path

app_name = "core"

urlpatterns: list = [
    # path("", views.placeholder, name="placeholder"),
]

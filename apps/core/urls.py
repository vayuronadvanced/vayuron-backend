"""
URL routes for the 'core' app.
"""

from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("health/", views.health_check, name="health"),
]

# Registered separately, under its own "search" namespace (not "core"'s),
# so the public-facing URL is the clean /api/search/ recommended in the
# search feature analysis, and so it doesn't collide with the "core"
# namespace already used by urlpatterns above — reusing the same namespace
# string across two different include() calls silently breaks reverse() for
# one of them. The view itself still lives in apps/core for code
# organization (core is the existing home for shared, cross-cutting
# endpoints that don't belong to one domain app); only the URL/namespace is
# separate. Reverse as reverse("search:global-search").
search_urlpatterns = [
    path("search/", views.GlobalSearchView.as_view(), name="global-search"),
]

from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/accounts/", include("apps.accounts.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/blog/", include("apps.blog.urls")),
    path("api/careers/", include("apps.careers.urls")),
    path("api/contacts/", include("apps.contacts.urls")),
    path("api/core/", include("apps.core.urls")),
    path("api/newsletter/", include("apps.newsletter.urls")),
    path("api/quotations/", include("apps.quotations.urls")),
    path("api/uploads/", include("apps.uploads.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
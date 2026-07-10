from django.contrib import admin

from .models import BusinessEvent


@admin.register(BusinessEvent)
class BusinessEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "source_page", "created_at")
    list_filter = ("event_type",)

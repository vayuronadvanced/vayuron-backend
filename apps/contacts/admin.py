from django.contrib import admin

from .models import ContactEnquiry


@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "phone_number", "company", "message")

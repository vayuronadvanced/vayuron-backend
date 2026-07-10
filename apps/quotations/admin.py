from django.contrib import admin

from .models import QuotationRequest


@admin.register(QuotationRequest)
class QuotationRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "product_or_sector", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "company", "product_or_sector")

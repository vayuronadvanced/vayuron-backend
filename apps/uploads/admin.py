from django.contrib import admin

from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("original_filename", "file_type", "uploaded_by", "created_at")
    list_filter = ("file_type",)
    search_fields = ("original_filename", "description")

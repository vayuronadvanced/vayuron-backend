from django.contrib import admin

from .models import JobListing, JobApplication


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "location", "status", "created_at")
    list_filter = ("status", "department")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "job_listing", "status", "created_at")
    list_filter = ("status", "job_listing")
    search_fields = ("full_name", "email")

from django.contrib import admin
from django.utils import timezone

from .models import ContactEnquiry, Question


@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "phone_number", "company", "message")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "name", "email", "status", "published_at", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("question_text", "answer_text", "name", "email")
    readonly_fields = ("created_at", "updated_at", "published_at")
    fields = (
        "question_text",
        "name",
        "email",
        "answer_text",
        "status",
        "published_at",
        "created_at",
        "updated_at",
    )
    actions = ["publish_selected"]

    @admin.action(description="Publish selected questions (requires an answer)")
    def publish_selected(self, request, queryset):
        answerable = queryset.exclude(answer_text="")
        skipped = queryset.count() - answerable.count()
        for question in answerable:
            question.publish()
        if skipped:
            self.message_user(
                request,
                f"Published {answerable.count()} question(s). "
                f"Skipped {skipped} without an answer_text.",
            )
        else:
            self.message_user(request, f"Published {answerable.count()} question(s).")

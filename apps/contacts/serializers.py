from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import ContactEnquiry, Question


class ContactEnquirySerializer(serializers.ModelSerializer):
    """Public-facing: used when a visitor submits the contact form."""

    class Meta:
        model = ContactEnquiry
        fields = [
            "id", "name", "email", "phone_number", "company",
            "subject", "message", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        # Business rule: block accidental/spam double-submits — same email +
        # same message within the last 5 minutes is rejected.
        recent_cutoff = timezone.now() - timedelta(minutes=5)
        duplicate_exists = ContactEnquiry.objects.filter(
            email=attrs.get("email"),
            message=attrs.get("message"),
            created_at__gte=recent_cutoff,
        ).exists()
        if duplicate_exists:
            raise serializers.ValidationError(
                "This enquiry looks like a duplicate of one submitted moments "
                "ago. Please wait a few minutes before resubmitting."
            )
        return attrs


class ContactEnquiryAdminSerializer(serializers.ModelSerializer):
    """Staff-facing: full record including status/assignment/internal notes."""

    class Meta:
        model = ContactEnquiry
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class QuestionSubmitSerializer(serializers.ModelSerializer):
    """Public-facing: used when a visitor submits a question to be answered."""

    class Meta:
        model = Question
        fields = ["id", "name", "email", "question_text", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        # Same anti-spam rule as the contact form: block accidental/spam
        # double-submits of the identical question within 5 minutes.
        recent_cutoff = timezone.now() - timedelta(minutes=5)
        duplicate_exists = Question.objects.filter(
            email=attrs.get("email"),
            question_text=attrs.get("question_text"),
            created_at__gte=recent_cutoff,
        ).exists()
        if duplicate_exists:
            raise serializers.ValidationError(
                "This question looks like a duplicate of one submitted "
                "moments ago. Please wait a few minutes before resubmitting."
            )
        return attrs


class QuestionPublicSerializer(serializers.ModelSerializer):
    """Public-facing: read-only view of a published FAQ entry (question + answer)."""

    class Meta:
        model = Question
        fields = ["id", "question_text", "answer_text", "published_at"]


class QuestionAdminSerializer(serializers.ModelSerializer):
    """Staff-facing: full record, used to edit/answer/publish a question."""

    class Meta:
        model = Question
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "published_at"]

from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import ContactEnquiry


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

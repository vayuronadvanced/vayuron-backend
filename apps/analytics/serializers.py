from rest_framework import serializers

from .models import BusinessEvent


class BusinessEventSerializer(serializers.ModelSerializer):
    """Public-facing: lets the frontend log a conversion event."""

    class Meta:
        model = BusinessEvent
        fields = ["id", "event_type", "source_page", "metadata", "created_at"]
        read_only_fields = ["id", "created_at"]

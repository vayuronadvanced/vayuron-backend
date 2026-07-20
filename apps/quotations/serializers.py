from rest_framework import serializers

from .models import QuotationRequest


class QuotationRequestSerializer(serializers.ModelSerializer):
    """Public-facing: used when a visitor submits a quotation request."""

    class Meta:
        model = QuotationRequest
        fields = [
            "id", "name", "email", "phone_number", "company",
            "product_or_sector", "requirements", "quantity", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class QuotationRequestAdminSerializer(serializers.ModelSerializer):
    """Staff-facing: full record including status/assignment/quoted amount."""

    class Meta:
        model = QuotationRequest
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

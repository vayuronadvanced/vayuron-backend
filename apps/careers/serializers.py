from rest_framework import serializers

from .models import JobApplication, JobListing


class JobListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobListing
        fields = [
            "id", "title", "slug", "department", "location",
            "employment_type", "description", "requirements",
            "status", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class JobApplicationSerializer(serializers.ModelSerializer):
    """Public-facing: used when a candidate applies to a job listing."""

    class Meta:
        model = JobApplication
        fields = [
            "id", "job_listing", "full_name", "email", "phone_number",
            "education", "experience", "skills", "cover_letter",
            "resume", "certificate", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        # Business rule: one active application per candidate per listing.
        # A prior rejected application doesn't block reapplying.
        existing = JobApplication.objects.filter(
            job_listing=attrs.get("job_listing"),
            email=attrs.get("email"),
        ).exclude(status=JobApplication.Status.REJECTED)
        if existing.exists():
            raise serializers.ValidationError(
                "An application from this email already exists for this "
                "position and is still being reviewed."
            )
        return attrs


class JobApplicationAdminSerializer(serializers.ModelSerializer):
    """Staff-facing: full record including status/internal notes."""

    class Meta:
        model = JobApplication
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

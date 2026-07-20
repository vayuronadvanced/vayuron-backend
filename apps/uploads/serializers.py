from rest_framework import serializers

from .models import UploadedFile


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = [
            "id", "file", "original_filename", "file_type",
            "size_bytes", "uploaded_by", "description", "created_at",
        ]
        read_only_fields = ["id", "uploaded_by", "original_filename", "size_bytes", "created_at"]

from rest_framework import viewsets
from rest_framework.parsers import FormParser, MultiPartParser

from apps.core.permissions import IsAdminOrEmployee

from .models import UploadedFile
from .serializers import UploadedFileSerializer


class UploadedFileViewSet(viewsets.ModelViewSet):
    """Staff-only: manage standalone uploaded files (brochures, misc. docs)."""

    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminOrEmployee]

    def perform_create(self, serializer):
        uploaded = self.request.FILES.get("file")
        serializer.save(
            uploaded_by=self.request.user,
            original_filename=getattr(uploaded, "name", ""),
            size_bytes=getattr(uploaded, "size", None),
        )

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.throttling import ScopedRateThrottle

from apps.core.permissions import IsAdminOrEmployee

from .models import JobApplication, JobListing
from .serializers import (
    JobApplicationAdminSerializer,
    JobApplicationSerializer,
    JobListingSerializer,
)


class JobListingViewSet(viewsets.ModelViewSet):
    """
    list/retrieve: public (visitors browsing open positions).
    create/update/delete: staff only.
    """

    queryset = JobListing.objects.all()
    serializer_class = JobListingSerializer
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", "department"]
    search_fields = ["title", "description"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [IsAdminOrEmployee()]


class JobApplicationViewSet(viewsets.ModelViewSet):
    """
    create: open to anyone (public application submission with resume upload).
    list/retrieve/update/delete: staff only.
    """

    queryset = JobApplication.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", "job_listing"]
    search_fields = ["full_name", "email"]

    def get_throttles(self):
        if self.action == "create":
            self.throttle_scope = "public_submission"
            return [ScopedRateThrottle()]
        return []

    def get_serializer_class(self):
        if self.action == "create":
            return JobApplicationSerializer
        return JobApplicationAdminSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [IsAdminOrEmployee()]

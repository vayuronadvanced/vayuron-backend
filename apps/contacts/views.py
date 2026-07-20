from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.throttling import ScopedRateThrottle

from apps.core.permissions import IsAdminOrEmployee

from .models import ContactEnquiry
from .serializers import ContactEnquiryAdminSerializer, ContactEnquirySerializer


class ContactEnquiryViewSet(viewsets.ModelViewSet):
    """
    create: open to anyone (public contact form submission).
    list/retrieve/update/delete: staff only (Admin or Employee).
    """

    queryset = ContactEnquiry.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["name", "email", "company", "message"]

    def get_throttles(self):
        if self.action == "create":
            self.throttle_scope = "public_submission"
            return [ScopedRateThrottle()]
        return []

    def get_serializer_class(self):
        if self.action == "create":
            return ContactEnquirySerializer
        return ContactEnquiryAdminSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [IsAdminOrEmployee()]

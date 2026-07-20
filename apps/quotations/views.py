from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.throttling import ScopedRateThrottle

from apps.core.permissions import IsAdminOrEmployee

from .models import QuotationRequest
from .serializers import QuotationRequestAdminSerializer, QuotationRequestSerializer


class QuotationRequestViewSet(viewsets.ModelViewSet):
    queryset = QuotationRequest.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", "product_or_sector"]
    search_fields = ["name", "email", "company", "product_or_sector"]

    def get_throttles(self):
        if self.action == "create":
            self.throttle_scope = "public_submission"
            return [ScopedRateThrottle()]
        return []

    def get_serializer_class(self):
        if self.action == "create":
            return QuotationRequestSerializer
        return QuotationRequestAdminSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [IsAdminOrEmployee()]

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets

from apps.core.permissions import IsAdminOrEmployee

from .models import BusinessEvent
from .serializers import BusinessEventSerializer


class BusinessEventViewSet(viewsets.ModelViewSet):
    """
    create: open to anyone (frontend logs conversion events as they happen).
    list/retrieve/update/delete: staff only (used for BI/reporting, Phase 7.2).
    """

    queryset = BusinessEvent.objects.all()
    serializer_class = BusinessEventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["event_type"]

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [IsAdminOrEmployee()]

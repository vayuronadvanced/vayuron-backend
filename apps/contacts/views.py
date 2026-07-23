from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.core.permissions import IsAdminOrEmployee

from .models import ContactEnquiry, Question
from .serializers import (
    ContactEnquiryAdminSerializer,
    ContactEnquirySerializer,
    QuestionAdminSerializer,
    QuestionPublicSerializer,
    QuestionSubmitSerializer,
)


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


class QuestionViewSet(viewsets.ModelViewSet):
    """
    Ask a Question (Contact page FAQ feature).

    create: open to anyone (public "Ask a Question" form submission).
    list/retrieve: public visitors only ever see status=published entries
        (enforced in get_queryset); staff see everything, including pending.
    update/destroy/publish: staff only (Admin or Employee) — used to edit,
        answer, and publish a question from the admin.
    """

    queryset = Question.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["question_text", "answer_text", "name", "email"]

    def get_queryset(self):
        qs = Question.objects.all()
        if self.request.user.is_authenticated and self.request.user.role in (
            "admin",
            "employee",
        ):
            return qs
        return qs.filter(status=Question.Status.PUBLISHED).order_by("-published_at")

    def get_throttles(self):
        if self.action == "create":
            self.throttle_scope = "public_submission"
            return [ScopedRateThrottle()]
        return []

    def get_serializer_class(self):
        if self.action == "create":
            return QuestionSubmitSerializer
        if self.action in ("list", "retrieve") and not (
            self.request.user.is_authenticated
            and self.request.user.role in ("admin", "employee")
        ):
            return QuestionPublicSerializer
        return QuestionAdminSerializer

    def get_permissions(self):
        if self.action in ("create", "list", "retrieve"):
            return [permissions.AllowAny()]
        return [IsAdminOrEmployee()]

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrEmployee])
    def publish(self, request, pk=None):
        question = self.get_object()
        question.publish()
        return Response(QuestionAdminSerializer(question).data)

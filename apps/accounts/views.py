"""
Auth and account views: registration, current-user endpoint, and admin-only
user management. Login/refresh/verify build on rest_framework_simplejwt's
built-in views, wired in urls.py.
"""

from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.core.permissions import IsAdmin

from .emails import send_password_reset_email, send_verification_email
from .models import User
from .serializers import (
    AdminUserSerializer,
    EmailVerificationConfirmSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    Public self-registration. Always creates a Customer-role account.
    Rate-limited like every other public-write endpoint (Phase 2.5) to
    curb spam account creation.
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "public_submission"

    def perform_create(self, serializer):
        user = serializer.save()
        send_verification_email(user)


class PasswordResetRequestView(APIView):
    """
    Public: kicks off the forgot-password flow. Always returns 200 with a
    generic message whether or not the email matches an account, so the
    endpoint can't be used to enumerate registered addresses.
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "public_submission"

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email__iexact=serializer.validated_data["email"]).first()
        if user is not None:
            send_password_reset_email(user)
        return Response(
            {"detail": "If an account exists for that email, a reset link has been sent."}
        )


class PasswordResetConfirmView(APIView):
    """Public: consumes the {uid, token} pair from the emailed link and sets
    the new password."""

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "public_submission"

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset. You can now log in."})


class ResendVerificationView(APIView):
    """Public: re-sends the verification email. Same anti-enumeration
    behaviour as password reset — always 200."""

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "public_submission"

    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            email__iexact=serializer.validated_data["email"], is_email_verified=False
        ).first()
        if user is not None:
            send_verification_email(user)
        return Response(
            {"detail": "If an unverified account exists for that email, a link has been sent."}
        )


class EmailVerificationConfirmView(APIView):
    """Public: consumes the {uid, token} pair from the emailed link and
    marks the account verified."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Email verified successfully."})


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """
    Same as simplejwt's TokenObtainPairView, with a strict rate limit added.
    Login is a brute-force target in a way the other public endpoints
    aren't (an attacker guessing passwords, not just spamming forms), so
    it gets its own tighter "login" scope rather than reusing
    "public_submission" (10/hour would be too loose here, and too strict
    for a legitimate user who mistypes their password a couple of times).
    """

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


class MeView(APIView):
    """
    Returns (and allows partial update of) the currently authenticated user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """
    Admin-only: list/manage all user accounts, including changing roles
    (e.g. promoting a Customer to Employee). Self-registration (public,
    always Customer) goes through RegisterView instead — this is the
    internal management surface for Phase 4.1's User Management dashboard.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]

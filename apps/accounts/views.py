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

from .models import User
from .serializers import AdminUserSerializer, RegisterSerializer, UserSerializer


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

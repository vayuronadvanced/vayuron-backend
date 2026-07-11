"""
Auth and account views: registration, current-user endpoint, and admin-only
user management. Login/refresh/verify are handled directly by
rest_framework_simplejwt's built-in views, wired in urls.py.
"""

from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin

from .models import User
from .serializers import AdminUserSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """
    Public self-registration. Always creates a Customer-role account.
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


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

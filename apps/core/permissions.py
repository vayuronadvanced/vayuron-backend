"""
Shared role-based DRF permission classes, built on accounts.User.Role.
Import these into any app's views.py rather than redefining role checks.
"""

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "employee"
        )


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "customer"
        )


class IsAdminOrEmployee(BasePermission):
    """Staff-side permission: internal dashboard access (Admin or Employee)."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("admin", "employee")
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: allows access if the requesting user owns the
    object (via an `owner`/`user` attribute) or is an Admin.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.role == "admin":
            return True
        owner = getattr(obj, "owner", None) or getattr(obj, "user", None)
        return owner == request.user

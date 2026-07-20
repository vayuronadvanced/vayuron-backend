"""
DRF serializers for authentication and account management.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from .tokens import email_verification_token_generator, password_reset_token_generator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone_number",
            "date_joined",
        ]
        read_only_fields = ["id", "role", "date_joined"]


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Admin-only variant: role IS writable here (unlike the self-service
    UserSerializer above), so admins can promote/demote accounts via the
    User Management dashboard (Phase 4.1.3).
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone_number",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone_number",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        # Public self-registration is always a Customer account. Admin/Employee
        # accounts are provisioned separately (Django admin or a future
        # internal-only endpoint), never through this public serializer.
        user = User(**validated_data, role=User.Role.CUSTOMER)
        user.set_password(password)
        user.save()
        return user


def _get_user_from_uid(uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


class PasswordResetRequestSerializer(serializers.Serializer):
    """Accepts an email address. Always succeeds from the caller's point of
    view (see the view) so the endpoint can't be used to enumerate which
    addresses have accounts."""

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate(self, attrs):
        user = _get_user_from_uid(attrs["uid"])
        if user is None or not password_reset_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError(
                {"token": "This password reset link is invalid or has expired."}
            )
        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class EmailVerificationConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        user = _get_user_from_uid(attrs["uid"])
        if user is None or not email_verification_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError(
                {"token": "This verification link is invalid or has expired."}
            )
        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        return user

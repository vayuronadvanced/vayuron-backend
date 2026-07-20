"""
URL routes for the 'accounts' app: registration, current-user, admin user
management, and JWT token obtain/refresh/verify (delegated to
rest_framework_simplejwt).
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    EmailVerificationConfirmView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    ResendVerificationView,
    ThrottledTokenObtainPairView,
    UserViewSet,
)

app_name = "accounts"

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("token/", ThrottledTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "email-verification/resend/",
        ResendVerificationView.as_view(),
        name="email_verification_resend",
    ),
    path(
        "email-verification/confirm/",
        EmailVerificationConfirmView.as_view(),
        name="email_verification_confirm",
    ),
    path("", include(router.urls)),
]

"""
Email senders for account verification and password reset.

Both build a frontend URL (not a backend/admin URL) since the actual
form the user fills in lives in the React app — see
frontend/src/pages/mainpages/VerifyEmailPage.jsx and
ResetPasswordPage.jsx. In development EMAIL_BACKEND is the console
backend (settings/development.py), so these just print to the
runserver terminal instead of actually sending.
"""

from django.conf import settings
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import email_verification_token_generator, password_reset_token_generator


def _uid(user):
    return urlsafe_base64_encode(force_bytes(user.pk))


def send_verification_email(user):
    token = email_verification_token_generator.make_token(user)
    link = f"{settings.FRONTEND_URL}/verify-email/{_uid(user)}/{token}/"
    send_mail(
        subject="Verify your Vayuron Advanced Systems account",
        message=(
            f"Hi {user.first_name or user.username},\n\n"
            f"Please verify your email address by visiting the link below:\n{link}\n\n"
            "If you did not create this account, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def send_password_reset_email(user):
    token = password_reset_token_generator.make_token(user)
    link = f"{settings.FRONTEND_URL}/reset-password/{_uid(user)}/{token}/"
    send_mail(
        subject="Reset your Vayuron Advanced Systems password",
        message=(
            f"Hi {user.first_name or user.username},\n\n"
            f"Someone requested a password reset for this account. If that was you, "
            f"set a new password here:\n{link}\n\n"
            "This link expires after a short time. If you did not request this, "
            "you can safely ignore this email — your password will not change."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )

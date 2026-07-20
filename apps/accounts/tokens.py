"""
Token generators for the password-reset and email-verification flows.

Both reuse Django's battle-tested PasswordResetTokenGenerator machinery
(itsdangerous-style, time-limited, invalidated automatically once the
field it hashes changes) rather than inventing custom token storage.
"""

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Same mechanism as Django's password-reset tokens, but the hash also
    mixes in `is_email_verified`. That means a token becomes invalid the
    moment the address is verified, so a link can't be replayed.
    """

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_email_verified}{user.email}"


password_reset_token_generator = PasswordResetTokenGenerator()
email_verification_token_generator = EmailVerificationTokenGenerator()

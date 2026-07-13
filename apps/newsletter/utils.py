"""
Signed unsubscribe token helpers.

Uses Django's own signing framework (no extra dependency) so an unsubscribe
link can safely identify a subscriber without requiring them to log in or
exposing a raw database ID that could be enumerated.
"""

from django.core import signing

SALT = "newsletter-unsubscribe"


def generate_unsubscribe_token(subscriber_id: int) -> str:
    return signing.dumps(subscriber_id, salt=SALT)


def verify_unsubscribe_token(token: str, max_age_seconds: int = 60 * 60 * 24 * 90):
    """
    Returns the subscriber_id if the token is valid and not expired
    (default max age: 90 days), otherwise raises signing.BadSignature or
    signing.SignatureExpired — callers should catch these.
    """
    return signing.loads(token, salt=SALT, max_age=max_age_seconds)

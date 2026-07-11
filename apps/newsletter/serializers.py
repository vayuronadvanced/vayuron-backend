from rest_framework import serializers

from .models import NewsletterCampaign, NewsletterSubscriber


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    """Public-facing: used for the newsletter signup form."""

    # DRF's ModelSerializer auto-adds a UniqueValidator here because the
    # model field is unique=True — which would reject a resubscribe attempt
    # at validation time, before create() below ever runs. The reactivation
    # business rule (Phase 2.5) needs to see already-used emails, so the
    # auto-validator is disabled and uniqueness is instead enforced by the
    # get_or_create()/is_active branching in create().
    email = serializers.EmailField(validators=[])

    class Meta:
        model = NewsletterSubscriber
        fields = ["id", "email", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        # Business rule: if this email previously unsubscribed, reactivate
        # the existing record instead of erroring on the unique constraint.
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=validated_data["email"],
            defaults={"is_active": True},
        )
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.unsubscribed_at = None
            subscriber.save(update_fields=["is_active", "unsubscribed_at"])
        elif not created and subscriber.is_active:
            raise serializers.ValidationError(
                {"email": "This email is already subscribed."}
            )
        return subscriber


class NewsletterSubscriberAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class NewsletterCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterCampaign
        fields = "__all__"
        read_only_fields = [
            "id", "created_at", "updated_at", "sent_at",
            "sent_by", "recipient_count", "status",
        ]

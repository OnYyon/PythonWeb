from rest_framework import serializers

from src.cinema_platform_django.subscription.domain.entities.subscription import (
    PaymentStatus,
    Subscription,
    SubscriptionStatus,
)


class SubscriptionCreateSerializer(serializers.Serializer):
    plan_id = serializers.UUIDField()


# TODO: use serializers.ModelSerializer
class SubscrptionSerializer(serializers.Serializer):
    """
    Превращает доменный Subscription (dataclass) в JSON-словар
    Используется для ответа на GET /subscriptions/{id}/ и для списков.
    """

    sub_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    plan_id = serializers.UUIDField()
    status = serializers.CharField()
    payment_status = serializers.CharField()
    started_at = serializers.DateTimeField(allow_null=True)
    expires_at = serializers.DateTimeField(allow_null=True)
    cancelled_at = serializers.DateTimeField(allow_null=True)
    transaction_id = serializers.CharField(allow_null=True)
    auto_renew = serializers.BooleanField()
    created_at = serializers.DateTimeField()

    def to_representation(self, instance: Subscription):
        return {
            "sub_id": str(instance.sub_id),
            "user_id": str(instance.user_id),
            "plan_id": str(instance.plan_id),
            "status": instance.status.value
            if isinstance(instance.status, SubscriptionStatus)
            else instance.status,
            "payment_status": instance.payment_status.value
            if isinstance(instance.payment_status, PaymentStatus)
            else instance.payment_status,
            "started_at": instance.started_at,
            "expires_at": instance.expires_at,
            "cancelled_at": instance.cancelled_at,
            "transaction_id": instance.transaction_id,
            "auto_renew": instance.auto_renew,
            "created_at": instance.created_at,
        }

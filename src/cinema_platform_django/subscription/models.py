from datetime import timedelta
from uuid import uuid4

from django.db import models


class SubscriptionModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    user_id = models.UUIDField()
    plan_id = models.UUIDField()

    status = models.CharField(
        max_length=20,
        default="pending",
    )
    payment_status = models.CharField(
        max_length=20,
        default="unpaid",
    )

    started_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    amount_paid = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=2
    )
    transaction_id = models.CharField(max_length=255, blank=True, db_index=True)
    auto_renew = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Subscriptions"


class PlanModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField()
    duration = models.DurationField(default=timedelta(days=30))

    class Meta:
        db_table = "SubscriptionsPlans"

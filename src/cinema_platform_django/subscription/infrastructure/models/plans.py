from datetime import timedelta
from uuid import uuid4

from django.db import models


class PlanModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField(default=timedelta(days=30))
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "SubscriptionsPlans"
        app_label = "subscription"

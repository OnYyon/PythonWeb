from django.contrib import admin

from src.cinema_platform_django.subscription.infrastructure.models import (
    PlanModel,
    SubscriptionModel,
)

admin.site.register(SubscriptionModel)
admin.site.register(PlanModel)

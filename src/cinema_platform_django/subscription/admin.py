from django.contrib import admin

from src.cinema_platform_django.subscription.models import SubscriptionModel, PlanModel


admin.site.register(SubscriptionModel)
admin.site.register(PlanModel)

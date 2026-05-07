from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.cinema_platform_django.subscription.api.v1.plans.views import (
    AdminPlanViewSet,
    PublicPlanViewSet,
)
from src.cinema_platform_django.subscription.api.v1.subscrption.views import (
    AdminSubscriptionViewSet,
    SubscrptionViews,
)

public_router = DefaultRouter()
public_router.register(r"plans", PublicPlanViewSet, basename="public-plans")
public_router.register(
    r"subscriptions", SubscrptionViews, basename="public-subscriptions"
)

admin_router = DefaultRouter()
admin_router.register(r"plans", AdminPlanViewSet, basename="admin-plans")
admin_router.register(
    r"subscriptions", AdminSubscriptionViewSet, basename="admin-subscriptions"
)

urlpatterns = [
    path("", include(public_router.urls)),
    path("admin/", include(admin_router.urls)),
]

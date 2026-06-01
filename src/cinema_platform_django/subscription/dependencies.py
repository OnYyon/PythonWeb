from functools import lru_cache

from src.cinema_platform_django.subscription.infrastructure.repository import (
    DjangoPlanRepository,
    DjangoSubRepository,
)
from src.cinema_platform_django.subscription.services.plan import PlanService
from src.cinema_platform_django.subscription.services.subscription import (
    SubscriptionService,
)
from src.shared.payment import PaymentGateway

_sub_repo = DjangoSubRepository()
_plan_repo = DjangoPlanRepository()


@lru_cache
def get_payment_gateway() -> PaymentGateway:
    return PaymentGateway()


@lru_cache
def get_subscription_service() -> SubscriptionService:
    """
    Возвращает готовый к использованию экземпляр SubscriptionService
    со всеми внедренными зависимостями.
    """
    return SubscriptionService(
        sub_repo=_sub_repo,
        plan_repo=_plan_repo,
        payment_gateway=get_payment_gateway(),
    )


@lru_cache
def get_plan_service() -> PlanService:
    """
    Возвращает готовый к использованию экземпляр PlanService
    со всеми внедренными зависимостями.
    """
    return PlanService(plan_repo=_plan_repo)

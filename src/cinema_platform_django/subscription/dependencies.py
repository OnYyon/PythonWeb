from src.cinema_platform_django.subscription.infrastructure.repository import (
    DjangoPlanRepository,
    DjangoSubRepository,
)
from src.cinema_platform_django.subscription.services.plan import PlanService
from src.cinema_platform_django.subscription.services.subscription import (
    SubscriptionService,
)

_sub_repo = DjangoSubRepository()
_plan_repo = DjangoPlanRepository()

_subscription_service = SubscriptionService(sub_repo=_sub_repo, plan_repo=_plan_repo)
_plan_service = PlanService(plan_repo=_plan_repo)


def get_subscription_service() -> SubscriptionService:
    """
    Возвращает готовый к использованию экземпляр SubscriptionService
    со всеми внедренными зависимостями.
    """
    return _subscription_service


def get_plan_service() -> PlanService:
    """
    Возвращает готовый к использованию экземпляр PlanService
    со всеми внедренными зависимостями.
    """
    return _plan_service

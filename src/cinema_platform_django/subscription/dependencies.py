from src.cinema_platform_django.subscription.infrastructure.repository import (
    DjangoPlanRepository,
    DjangoSubRepository,
)
from src.cinema_platform_django.subscription.services.plan import PlanService
from src.cinema_platform_django.subscription.services.subscrption import (
    SubscrptionService,
)

_sub_repo = DjangoSubRepository()
_plan_repo = DjangoPlanRepository()

_subscription_service = SubscrptionService(sub_repo=_sub_repo, plan_repo=_plan_repo)
_plan_service = PlanService(plan_repo=_plan_repo)


def get_subscription_service() -> SubscrptionService:
    """
    Возвращает готовый к использованию экземпляр SubscrptionService
    со всеми внедренными зависимостями.
    """
    return _subscription_service


def get_plan_service() -> PlanService:
    """
    Возвращает готовый к использованию экземпляр PlanService
    со всеми внедренными зависимостями.
    """
    return _plan_service

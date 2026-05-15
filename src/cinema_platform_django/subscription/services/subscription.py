from uuid import UUID

from src.cinema_platform_django.subscription.domain.entities.subscription import (
    PaymentStatus,
    Subscription,
)
from src.cinema_platform_django.subscription.domain.repositories.interfaces import (
    PlanRepositoryABC,
    SubRepositoryABC,
)
from src.cinema_platform_django.subscription.services.exceptions import (
    PlanNotFoundError,
    SubscriptionAlreadyActiveError,
    SubscriptionNotFoundError,
    SubscriptionRenewalNotAllowedError,
)


class SubscriptionService:
    def __init__(
        self, sub_repo: SubRepositoryABC, plan_repo: PlanRepositoryABC
    ) -> None:
        self.sub_repo = sub_repo
        self.plan_repo = plan_repo

    def create(
        self, user_id: UUID, plan_id: UUID, auto_renew: bool = False
    ) -> Subscription:
        active_sub = self.sub_repo.get_active_for_user(user_id)
        if active_sub:
            raise SubscriptionAlreadyActiveError(user_id)

        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise PlanNotFoundError(plan_id)

        sub = Subscription(user_id, plan_id, auto_renew=auto_renew)
        return self.sub_repo.create(sub)

    def get_by_id(self, sub_id: UUID) -> Subscription:
        sub = self.sub_repo.get_by_id(sub_id)
        if not sub:
            raise SubscriptionNotFoundError(sub_id)
        return sub

    def get_active_for_user(self, user_id: UUID) -> Subscription | None:
        return self.sub_repo.get_active_for_user(user_id)

    def get_user_history(self, user_id: UUID) -> list[Subscription]:
        return self.sub_repo.list_for_user(user_id)

    def get_all(self) -> list[Subscription]:
        return self.sub_repo.get_all()

    def activate(self, sub_id: UUID) -> Subscription:
        sub = self.sub_repo.get_by_id(sub_id)
        if not sub:
            raise SubscriptionNotFoundError(sub_id)

        plan = self.plan_repo.get_by_id(sub.plan_id)
        if not plan:
            raise PlanNotFoundError(sub.plan_id)

        sub.activate(plan.duration)
        return self.sub_repo.update(sub)

    def cancel(self, sub_id: UUID) -> Subscription:
        sub = self.sub_repo.get_by_id(sub_id)
        if not sub:
            raise SubscriptionNotFoundError(sub_id)
        sub.cancel()
        return self.sub_repo.update(sub)

    def renew(self, sub_id: UUID) -> Subscription:
        sub = self.sub_repo.get_by_id(sub_id)
        if not sub:
            raise SubscriptionNotFoundError(sub_id)

        plan = self.plan_repo.get_by_id(sub.plan_id)
        if not plan:
            raise PlanNotFoundError(sub.plan_id)

        is_renewed = sub.renew(plan.duration)
        if not is_renewed:
            raise SubscriptionRenewalNotAllowedError(sub_id)

        sub.payment_status = PaymentStatus.PAID
        return self.sub_repo.update(sub)

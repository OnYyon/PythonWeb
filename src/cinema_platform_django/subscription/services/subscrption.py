from uuid import UUID

from src.cinema_platform_django.subscription.domain.entities.subscription import (
    PaymentStatus,
    Subscription,
)
from src.cinema_platform_django.subscription.domain.repositories.interfaces import (
    PlanRepositoryABC,
    SubRepositoryABC,
)


class SubscrptionService:
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
            raise ValueError("User already has an active subscription")

        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")

        sub = Subscription(user_id, plan_id, auto_renew=auto_renew)
        return self.sub_repo.create(sub)

    def get_by_id(self, sub_id: UUID) -> Subscription | None:
        return self.sub_repo.get_by_id(sub_id)

    def get_user_history(self, user_id: UUID) -> list[Subscription]:
        return self.sub_repo.list_for_user(user_id)

    def get_all(self) -> list[Subscription]:
        return self.sub_repo.get_all()

    def activate(self, sub_id: UUID) -> Subscription:
        sub = self.sub_repo.get_by_id(sub_id)
        if not sub:
            raise ValueError("Not found")

        plan = self.plan_repo.get_by_id(sub.plan_id)
        if not plan:
            raise ValueError("Plan not found")

        sub.activate(plan.duration)
        return self.sub_repo.update(sub)

    def cancel(self, sub_id: UUID) -> Subscription:
        sub = self.sub_repo.get_by_id(sub_id)
        if not sub:
            raise ValueError("Not found")
        sub.cancel()
        return self.sub_repo.update(sub)

    def renew(self, sub_id: UUID) -> Subscription:
        sub = self.sub_repo.get_by_id(sub_id)
        if not sub:
            raise ValueError("Not found")

        plan = self.plan_repo.get_by_id(sub.plan_id)
        if not plan:
            raise ValueError("Plan not found")

        is_renewed = sub.renew(plan.duration)
        if not is_renewed:
            raise ValueError("Cannot renew this subscription (auto_renew is off)")

        sub.payment_status = PaymentStatus.PAID
        return self.sub_repo.update(sub)

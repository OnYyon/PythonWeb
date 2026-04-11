from datetime import timedelta
from decimal import Decimal
from uuid import UUID

from src.cinema_platform_django.subscription.domain.entities.plan import SubPlan
from src.cinema_platform_django.subscription.domain.repositories.interfaces import (
    PlanRepositoryABC,
)


class PlanService:
    def __init__(self, plan_repo: PlanRepositoryABC) -> None:
        self.plan_repo = plan_repo

    def create(
        self, name: str, price: Decimal, duration: timedelta | None = None
    ) -> SubPlan:
        existing_plan = self.plan_repo.get_by_name(name)
        if existing_plan:
            raise ValueError("Plan with this name already exists")

        if duration is None:
            plan = SubPlan(name=name, price=price)
        else:
            plan = SubPlan(name=name, price=price, duration=duration)

        return self.plan_repo.create(plan)

    def get_all(self) -> list[SubPlan]:
        return self.plan_repo.get_all()

    def get_by_id(self, plan_id: UUID) -> SubPlan | None:
        return self.plan_repo.get_by_id(plan_id)

    def delete(self, plan_id: UUID) -> None:
        self.plan_repo.delete(plan_id)

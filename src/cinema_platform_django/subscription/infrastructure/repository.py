from dataclasses import asdict
from typing import Any
from uuid import UUID

from src.cinema_platform_django.subscription.domain.entities.plan import SubPlan
from src.cinema_platform_django.subscription.domain.entities.subscription import (
    PaymentStatus,
    Subscription,
    SubscriptionStatus,
)
from src.cinema_platform_django.subscription.domain.repositories.interfaces import (
    PlanRepositoryABC,
    SubRepositoryABC,
)
from src.cinema_platform_django.subscription.models import PlanModel, SubscriptionModel


class DjangoSubRepository(SubRepositoryABC):
    def to_domain(self, model: SubscriptionModel) -> Subscription:
        return Subscription(
            user_id=model.user_id,
            plan_id=model.plan_id,
            sub_id=model.uuid,
            status=SubscriptionStatus(model.status),
            payment_status=PaymentStatus(model.payment_status),
            started_at=model.started_at,
            expires_at=model.expires_at,
            cancelled_at=model.cancelled_at,
            transaction_id=model.transaction_id,
            auto_renew=model.auto_renew,
            created_at=model.created_at,
        )

    def get_by_id(self, sub_id: UUID) -> Subscription | None:
        try:
            queryset = SubscriptionModel.objects.get(uuid=sub_id)
            return self.to_domain(queryset)
        except SubscriptionModel.DoesNotExist:
            return None

    def get_active_for_user(self, user_id: UUID) -> Subscription | None:
        try:
            queryset = SubscriptionModel.objects.get(user_id=user_id)
            return self.to_domain(queryset)
        except SubscriptionModel.DoesNotExist:
            return None

    def create(self, sub: Subscription) -> Subscription:
        data: dict[str, Any] = asdict(sub)
        data["status"] = sub.status.value
        data["payment_status"] = sub.payment_status.value
        data["uuid"] = data.pop("sub_id")
        SubscriptionModel.objects.create(**data)
        return sub

    def update(self, sub: Subscription) -> Subscription:
        data: dict[str, Any] = asdict(sub)
        data["status"] = sub.status.value
        data["payment_status"] = sub.payment_status.value
        sub_uuid = data.pop("sub_id")
        SubscriptionModel.objects.filter(uuid=sub_uuid).update(**data)
        return sub

    def list_for_user(self, user_id: UUID) -> list[Subscription]:
        qs = SubscriptionModel.objects.filter(user_id=user_id).order_by("-created_at")
        return [self.to_domain(m) for m in qs]

    def get_all(self) -> list[Subscription]:
        qs = SubscriptionModel.objects.all().order_by("-created_at")
        return [self.to_domain(m) for m in qs]


class DjangoPlanRepository(PlanRepositoryABC):
    def to_domain(self, plan: PlanModel) -> SubPlan:
        return SubPlan(
            name=plan.name,
            price=plan.price,
            duration=plan.duration,
            plan_id=plan.uuid,
        )

    def get_by_id(self, plan_id: UUID) -> SubPlan | None:
        try:
            queryset = PlanModel.objects.get(uuid=plan_id)
            return self.to_domain(queryset)
        except PlanModel.DoesNotExist:
            return None

    def get_by_name(self, name: str) -> SubPlan | None:
        try:
            queryset = PlanModel.objects.get(name=name)
            return self.to_domain(queryset)
        except PlanModel.DoesNotExist:
            return None

    def create(self, plan: SubPlan) -> SubPlan:
        data: dict[str, Any] = asdict(plan)
        data["uuid"] = data.pop("plan_id")
        PlanModel.objects.create(**data)
        return plan

    def update(self, plan: SubPlan) -> SubPlan:
        data: dict[str, Any] = asdict(plan)
        plan_uuid = data.pop("plan_id")
        PlanModel.objects.filter(uuid=plan_uuid).update(**data)
        return plan

    def get_all(self) -> list[SubPlan]:
        qs = PlanModel.objects.all()
        return [self.to_domain(m) for m in qs]

    def delete(self, plan_id: UUID) -> None:
        PlanModel.objects.filter(uuid=plan_id).delete()

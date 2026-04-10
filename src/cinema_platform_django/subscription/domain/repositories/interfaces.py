from abc import ABC, abstractmethod
from uuid import UUID

from src.cinema_platform_django.subscription.domain.entities.plan import SubPlan
from src.cinema_platform_django.subscription.domain.entities.subscription import (
    Subscription,
)


class SubRepositoryABC(ABC):
    @abstractmethod
    def get_by_id(self, sub_id: UUID) -> Subscription | None: ...

    @abstractmethod
    def get_active_for_user(self, user_id: UUID) -> Subscription | None: ...

    @abstractmethod
    def create(self, sub: Subscription) -> Subscription: ...

    @abstractmethod
    def update(self, sub: Subscription) -> Subscription: ...

    @abstractmethod
    def list_for_user(self, user_id: UUID) -> list[Subscription]: ...

    @abstractmethod
    def get_all(self) -> list[Subscription]: ...


class PlanRepositoryABC(ABC):
    @abstractmethod
    def get_by_id(self, plan_id: UUID) -> SubPlan | None: ...

    @abstractmethod
    def get_by_name(self, name: str) -> SubPlan | None: ...

    @abstractmethod
    def create(self, plan: SubPlan) -> SubPlan: ...

    @abstractmethod
    def update(self, plan: SubPlan) -> SubPlan: ...

    @abstractmethod
    def get_all(self) -> list[SubPlan]: ...

    @abstractmethod
    def delete(self, plan_id: UUID) -> None: ...

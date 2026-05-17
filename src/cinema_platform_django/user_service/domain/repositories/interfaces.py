from abc import ABC, abstractmethod
from collections.abc import Sequence
from types import EllipsisType
from typing import Protocol
from uuid import UUID

from src.cinema_platform_django.user_service.domain.entities import User
from src.cinema_platform_django.user_service.domain.sentinels import UNSET


class UserRepositoryABC(ABC):
    @abstractmethod
    def get(self, *, user_id: UUID) -> User | None: ...

    @abstractmethod
    def list(self) -> Sequence[User]: ...

    @abstractmethod
    def get_by_email(self, *, email: str) -> User | None: ...

    @abstractmethod
    def get_by_username(self, *, username: str) -> User | None: ...

    @abstractmethod
    def get_by_phone(self, *, phone: str) -> User | None: ...

    @abstractmethod
    def create(
        self,
        *,
        username: str,
        email: str,
        password_hash: str,
        full_name: str = "",
        phone: str | None = None,
    ) -> User: ...

    @abstractmethod
    def update(
        self,
        *,
        user_id: UUID,
        username: str | EllipsisType = UNSET,
        email: str | EllipsisType = UNSET,
        password_hash: str | EllipsisType = UNSET,
        full_name: str | EllipsisType = UNSET,
        phone: str | None | EllipsisType = UNSET,
    ) -> User | None: ...

    @abstractmethod
    def delete(self, *, user_id: UUID) -> None: ...


class PasswordHasher(Protocol):
    def hash(self, raw_password: str) -> str: ...

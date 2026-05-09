from collections.abc import Sequence
from uuid import UUID

from django.db import IntegrityError

from src.cinema_platform_django.user_service.domain.entities import (
    User as DomainUser,
    UserRole,
)
from src.cinema_platform_django.user_service.domain.exceptions import (
    UserAlreadyExistsError,
)
from src.cinema_platform_django.user_service.domain.repositories.interfaces import (
    UserRepositoryABC,
)
from src.cinema_platform_django.user_service.domain.sentinels import UNSET
from src.cinema_platform_django.user_service.infrastructure.models.user import (
    User as UserModel,
)


class DjangoUserRepository(UserRepositoryABC):
    def get(self, *, user_id: UUID) -> DomainUser | None:
        user = UserModel.objects.filter(uuid=user_id).first()
        return self._to_domain(user) if user is not None else None

    def list(self) -> Sequence[DomainUser]:
        return [
            self._to_domain(user)
            for user in UserModel.objects.all().order_by("-created_at")
        ]

    def get_by_email(self, *, email: str) -> DomainUser | None:
        user = UserModel.objects.filter(email=email).first()
        return self._to_domain(user) if user is not None else None

    def get_by_username(self, *, username: str) -> DomainUser | None:
        user = UserModel.objects.filter(username=username).first()
        return self._to_domain(user) if user is not None else None

    def get_by_phone(self, *, phone: str) -> DomainUser | None:
        user = UserModel.objects.filter(phone=phone).first()
        return self._to_domain(user) if user is not None else None

    def create(
        self,
        *,
        username: str,
        email: str,
        password_hash: str,
        full_name: str = "",
        phone: str | None = None,
    ) -> DomainUser:
        try:
            user = UserModel.objects.create(
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                phone=phone,
            )
        except IntegrityError as error:
            raise self._unique_error(error) from error
        return self._to_domain(user)

    def update(
        self,
        *,
        user_id: UUID,
        username: str | object = UNSET,
        email: str | object = UNSET,
        password_hash: str | object = UNSET,
        full_name: str | object = UNSET,
        phone: str | None | object = UNSET,
    ) -> DomainUser | None:
        values = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "phone": phone,
        }
        update_values = {
            field: value for field, value in values.items() if value is not UNSET
        }

        user = UserModel.objects.filter(uuid=user_id).first()
        if user is None:
            return None

        if update_values:
            for field, value in update_values.items():
                setattr(user, field, value)
            try:
                user.save(update_fields=[*update_values.keys(), "updated_at"])
            except IntegrityError as error:
                raise self._unique_error(error) from error

        return self._to_domain(user)

    def delete(self, *, user_id: UUID) -> None:
        UserModel.objects.filter(uuid=user_id).delete()

    @staticmethod
    def _to_domain(user: UserModel) -> DomainUser:
        return DomainUser(
            uuid=user.uuid,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=UserRole(user.role),
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @staticmethod
    def _unique_error(error: IntegrityError) -> UserAlreadyExistsError:
        message = str(error).lower()
        for field in ("email", "username", "phone"):
            if field in message:
                return UserAlreadyExistsError(field)
        return UserAlreadyExistsError("unique field")

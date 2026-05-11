from uuid import UUID

from src.cinema_platform_django.user_service.domain.exceptions import (
    UserAlreadyExistsError,
)
from src.cinema_platform_django.user_service.domain.repositories.interfaces import (
    UserRepositoryABC,
)


def ensure_unique_user_fields(
    repository: UserRepositoryABC,
    *,
    username: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    exclude_user_id: UUID | None = None,
) -> None:
    if username is not None:
        existing = repository.get_by_username(username=username)
        if existing is not None and existing.uuid != exclude_user_id:
            raise UserAlreadyExistsError("username")

    if email is not None:
        existing = repository.get_by_email(email=email)
        if existing is not None and existing.uuid != exclude_user_id:
            raise UserAlreadyExistsError("email")

    if phone:
        existing = repository.get_by_phone(phone=phone)
        if existing is not None and existing.uuid != exclude_user_id:
            raise UserAlreadyExistsError("phone")

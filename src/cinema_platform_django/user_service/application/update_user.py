from uuid import UUID

from src.cinema_platform_django.user_service.application.dto import (
    UNSET,
    UpdateUserCommand,
)
from src.cinema_platform_django.user_service.application.user_uniqueness import (
    ensure_unique_user_fields,
)
from src.cinema_platform_django.user_service.domain.entities import User
from src.cinema_platform_django.user_service.domain.exceptions import UserNotFoundError
from src.cinema_platform_django.user_service.domain.repositories.interfaces import (
    PasswordHasher,
    UserRepositoryABC,
)


class UpdateUserUseCase:
    def __init__(
        self,
        *,
        repository: UserRepositoryABC,
        password_hasher: PasswordHasher,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher

    def execute(self, user_id: UUID, command: UpdateUserCommand) -> User:
        if self._repository.get(user_id=user_id) is None:
            raise UserNotFoundError(user_id)

        ensure_unique_user_fields(
            self._repository,
            username=command.username if isinstance(command.username, str) else None,
            email=command.email if isinstance(command.email, str) else None,
            phone=command.phone if isinstance(command.phone, str) else None,
            exclude_user_id=user_id,
        )
        password_hash = UNSET
        if isinstance(command.password, str) and command.password:
            password_hash = self._password_hasher.hash(command.password)

        updated_user = self._repository.update(
            user_id=user_id,
            username=command.username,
            email=command.email,
            password_hash=password_hash,
            full_name=command.full_name,
            phone=command.phone,
        )
        if updated_user is None:
            raise UserNotFoundError(user_id)
        return updated_user

from uuid import UUID

from src.cinema_platform_django.user_service.domain.exceptions import UserNotFoundError
from src.cinema_platform_django.user_service.domain.repositories.interfaces import (
    UserRepositoryABC,
)


class DeleteUserUseCase:
    def __init__(self, *, repository: UserRepositoryABC) -> None:
        self._repository = repository

    def execute(self, user_id: UUID) -> None:
        if self._repository.get(user_id=user_id) is None:
            raise UserNotFoundError(user_id)
        self._repository.delete(user_id=user_id)

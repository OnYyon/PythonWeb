from uuid import UUID

from src.cinema_platform_django.user_service.domain.entities import User
from src.cinema_platform_django.user_service.domain.exceptions import UserNotFoundError
from src.cinema_platform_django.user_service.domain.repositories.interfaces import (
    UserRepositoryABC,
)


class GetUserUseCase:
    def __init__(self, *, repository: UserRepositoryABC) -> None:
        self._repository = repository

    def execute(self, user_id: UUID) -> User:
        user = self._repository.get(user_id=user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user

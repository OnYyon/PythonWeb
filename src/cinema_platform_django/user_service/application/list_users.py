from collections.abc import Sequence

from src.cinema_platform_django.user_service.domain.entities import User
from src.cinema_platform_django.user_service.domain.repositories.interfaces import (
    UserRepositoryABC,
)


class ListUsersUseCase:
    def __init__(self, *, repository: UserRepositoryABC) -> None:
        self._repository = repository

    def execute(self) -> Sequence[User]:
        return self._repository.list()

from src.cinema_platform_django.user_service.application.dto import CreateUserCommand
from src.cinema_platform_django.user_service.application.user_uniqueness import (
    ensure_unique_user_fields,
)
from src.cinema_platform_django.user_service.domain.entities import User
from src.cinema_platform_django.user_service.domain.repositories.interfaces import (
    PasswordHasher,
    UserRepositoryABC,
)


class CreateUserUseCase:
    def __init__(
        self,
        *,
        repository: UserRepositoryABC,
        password_hasher: PasswordHasher,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher

    def execute(self, command: CreateUserCommand) -> User:
        ensure_unique_user_fields(
            self._repository,
            username=command.username,
            email=command.email,
            phone=command.phone,
        )
        return self._repository.create(
            username=command.username,
            email=command.email,
            password_hash=self._password_hasher.hash(command.password),
            full_name=command.full_name,
            phone=command.phone,
        )


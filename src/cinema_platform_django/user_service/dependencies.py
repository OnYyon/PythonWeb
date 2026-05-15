from src.cinema_platform_django.user_service.application.create_user import (
    CreateUserUseCase,
)
from src.cinema_platform_django.user_service.application.delete_user import (
    DeleteUserUseCase,
)
from src.cinema_platform_django.user_service.application.get_user import GetUserUseCase
from src.cinema_platform_django.user_service.application.list_users import (
    ListUsersUseCase,
)
from src.cinema_platform_django.user_service.application.update_user import (
    UpdateUserUseCase,
)
from src.cinema_platform_django.user_service.infrastructure.repositories.django_repository import (
    DjangoUserRepository,
)
from src.cinema_platform_django.user_service.infrastructure.security.password_hasher import (
    DjangoPasswordHasher,
)


def create_user_use_case() -> CreateUserUseCase:
    return CreateUserUseCase(
        repository=DjangoUserRepository(),
        password_hasher=DjangoPasswordHasher(),
    )


def list_users_use_case() -> ListUsersUseCase:
    return ListUsersUseCase(repository=DjangoUserRepository())


def get_user_use_case() -> GetUserUseCase:
    return GetUserUseCase(repository=DjangoUserRepository())


def update_user_use_case() -> UpdateUserUseCase:
    return UpdateUserUseCase(
        repository=DjangoUserRepository(),
        password_hasher=DjangoPasswordHasher(),
    )


def delete_user_use_case() -> DeleteUserUseCase:
    return DeleteUserUseCase(repository=DjangoUserRepository())

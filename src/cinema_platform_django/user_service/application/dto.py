from dataclasses import dataclass

from src.cinema_platform_django.user_service.domain.sentinels import UNSET


@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    username: str
    email: str
    password: str
    full_name: str = ""
    phone: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateUserCommand:
    username: str | object = UNSET
    email: str | object = UNSET
    password: str | object = UNSET
    full_name: str | object = UNSET
    phone: str | None | object = UNSET

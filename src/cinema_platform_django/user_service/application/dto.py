from dataclasses import dataclass
from types import EllipsisType

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
    username: str | EllipsisType = UNSET
    email: str | EllipsisType = UNSET
    password: str | EllipsisType = UNSET
    full_name: str | EllipsisType = UNSET
    phone: str | None | EllipsisType = UNSET

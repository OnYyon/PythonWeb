from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class UserRole(StrEnum):
    USER = "user"


@dataclass(frozen=True, slots=True)
class User:
    uuid: UUID
    username: str
    email: str
    full_name: str
    phone: str | None
    role: UserRole
    created_at: datetime
    updated_at: datetime

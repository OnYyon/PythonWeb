from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class User:
    uuid: UUID
    username: str
    email: str
    full_name: str
    phone: str | None
    role: str
    created_at: datetime
    updated_at: datetime


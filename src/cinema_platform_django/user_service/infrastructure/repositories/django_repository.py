from typing import Any

from ...domain.repositories.interfaces import UserRepositoryABC
from ..models.user import User


class DjangoUserRepository(UserRepositoryABC):
    def get(self, *, entity_id: Any) -> User | None:
        return User.objects.filter(uuid=entity_id).first()

    def get_all(self) -> list[User]:
        return list(User.objects.all())

    def get_by_email(self, *, email: str) -> User | None:
        return User.objects.filter(email=email).first()

    def get_by_username(self, *, username: str) -> User | None:
        return User.objects.filter(username=username).first()

    def create(self, **kwargs: Any) -> User:  # исправлено под supertype
        return User.objects.create(**kwargs)

    def update(self, *, entity_id: Any, **kwargs: Any) -> User | None:
        User.objects.filter(uuid=entity_id).update(**kwargs)
        return self.get(entity_id=entity_id)

    def update_role(self, *, entity_id: Any, role: str) -> User | None:
        User.objects.filter(uuid=entity_id).update(role=role)
        return self.get(entity_id=entity_id)

    def delete(self, *, entity_id: Any) -> None:
        User.objects.filter(uuid=entity_id).delete()

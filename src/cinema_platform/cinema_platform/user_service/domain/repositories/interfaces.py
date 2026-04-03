from abc import ABC, abstractmethod
from typing import Any

class BaseRepositoryABC(ABC):
    @abstractmethod
    def get(self, *, entity_id: Any) -> Any:
        ...

    @abstractmethod
    def get_all(self) -> list:
        ...

    @abstractmethod
    def create(self, **kwargs) -> Any:
        ...

    @abstractmethod
    def update(self, *, entity_id: Any, **kwargs) -> Any:
        ...

    @abstractmethod
    def delete(self, *, entity_id: Any) -> None:
        ...


class UserRepositoryABC(BaseRepositoryABC, ABC):
    @abstractmethod
    def get_by_email(self, *, email: str) -> Any:
        ...

    @abstractmethod
    def get_by_username(self, *, username: str) -> Any:
        ...

    @abstractmethod
    def update_role(self, *, entity_id: Any, role: str) -> Any:
        ...

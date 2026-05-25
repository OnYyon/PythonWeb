from abc import ABC, abstractmethod
from uuid import UUID

from src.payment.domain.entities.card import Card
from src.payment.domain.entities.payment import Payment


class CardRepositoryABC(ABC):
    @abstractmethod
    async def get(self, card_id: UUID) -> Card | None: ...

    @abstractmethod
    async def get_for_update(self, card_id: UUID) -> Card | None: ...

    @abstractmethod
    async def list_for_user(self, user_id: UUID) -> list[Card]: ...

    @abstractmethod
    async def create(self, card: Card) -> Card: ...

    @abstractmethod
    async def update(self, card: Card) -> Card: ...


class PaymentRepositoryABC(ABC):
    @abstractmethod
    async def create(self, payment: Payment) -> Payment: ...

    @abstractmethod
    async def get(self, payment_id: UUID) -> Payment | None: ...

    @abstractmethod
    async def list_for_card(self, card_id: UUID) -> list[Payment]: ...

    @abstractmethod
    async def list_for_subscription(self, sub_id: UUID) -> list[Payment]: ...


class UnitOfWorkABC(ABC):
    cards: CardRepositoryABC
    payments: PaymentRepositoryABC

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWorkABC": ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb) -> None: ...

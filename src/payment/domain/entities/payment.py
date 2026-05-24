from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from src.payment.domain.exceptions import InvalidAmountError
from src.payment.domain.utils import hash_card_id, normalize_amount


class PaymentStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class CardRef:
    card_id: UUID | None
    card_hash: str

    @classmethod
    def from_id(cls, card_id: UUID) -> "CardRef":
        return cls(card_id=card_id, card_hash=hash_card_id(card_id))

    @classmethod
    def from_hash(cls, card_hash: str) -> "CardRef":
        return cls(card_id=None, card_hash=card_hash)


@dataclass(slots=True)
class Payment:
    sub_id: UUID
    amount: Decimal
    card: CardRef
    payment_id: UUID = field(default_factory=uuid4)
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self.amount = normalize_amount(self.amount)
        if self.amount <= 0:
            raise InvalidAmountError(self.amount)

    def mark_paid(self) -> None:
        self.status = PaymentStatus.PAID

    def mark_failed(self) -> None:
        self.status = PaymentStatus.FAILED

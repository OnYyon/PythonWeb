from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from src.payment.domain.exceptions import InsufficientFundsError, InvalidAmountError
from src.payment.domain.utils import normalize_amount


@dataclass(slots=True)
class Card:
    user_id: UUID
    balance: Decimal = Decimal("0.00")
    card_id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.balance = normalize_amount(self.balance)
        if self.balance < 0:
            raise InvalidAmountError(self.balance)

    def debit(self, amount: Decimal) -> None:
        amount = normalize_amount(amount)
        if amount <= 0:
            raise InvalidAmountError(amount)
        if self.balance < amount:
            raise InsufficientFundsError(self.card_id)
        self.balance = normalize_amount(self.balance - amount)

    def credit(self, amount: Decimal) -> None:
        amount = normalize_amount(amount)
        if amount <= 0:
            raise InvalidAmountError(amount)
        self.balance = normalize_amount(self.balance + amount)

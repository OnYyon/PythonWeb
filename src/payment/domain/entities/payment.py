from dataclasses import dataclass
from enum import Enum
from uuid import UUID, uuid4


class PaymentStatus(Enum):
    FAILED = 0
    SUCCESS = 1
    PENDING = 2


@dataclass
class Payment:
    sub_id: UUID
    amount: int
    card_hash: str
    status: PaymentStatus = PaymentStatus.PENDING
    payment_id: UUID = uuid4()

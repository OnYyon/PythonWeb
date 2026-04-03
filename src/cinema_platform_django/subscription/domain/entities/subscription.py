from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4


class SubscriptionStatus(Enum):
    """Все возможные статусы подписки"""

    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PaymentStatus(Enum):
    """Все возможные статусы оплатыд"""

    UNPAID = "unpaid"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class Subscription:
    user_id: UUID
    plan_id: UUID
    sub_id: UUID = field(default_factory=uuid4)
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.UNPAID
    started_at: datetime | None = None
    expires_at: datetime | None = None
    cancelled_at: datetime | None = None
    transaction_id: str | None = None
    auto_renew: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def activate(self):
        if self.status != SubscriptionStatus.PENDING:
            raise ValueError("")
        self.status = SubscriptionStatus.ACTIVE
        self.started_at = datetime.now(UTC)

    def cancel(self):
        self.status = SubscriptionStatus.CANCELLED
        self.cancelled_at = datetime.now(UTC)
        self.auto_renew = False


@dataclass
class SubPlan:
    name: str
    price: Decimal
    plan_id: UUID = field(default_factory=uuid4)
    duration: timedelta = field(default_factory=lambda: timedelta(days=30))

    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Price should be positive")

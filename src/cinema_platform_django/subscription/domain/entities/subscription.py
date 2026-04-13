from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4


class PaymentStatus(Enum):
    """Все возможные статусы оплаты"""

    UNPAID = "unpaid"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class SubscriptionStatus(Enum):
    """Все возможные статусы подписки"""

    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


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

    def activate(self, duration: timedelta):
        if self.status == SubscriptionStatus.ACTIVE:
            return
        # TODO: Add check to ensure payment_status == PaymentStatus.PAID before activating
        if self.status != SubscriptionStatus.PENDING:
            raise ValueError(
                f"Cannot activate subscription with status {self.status.value}"
            )
        self.status = SubscriptionStatus.ACTIVE
        self.started_at = datetime.now(UTC)
        self.expires_at = self.started_at + duration

    def cancel(self):
        self.status = SubscriptionStatus.CANCELLED
        self.cancelled_at = datetime.now(UTC)
        self.auto_renew = False

    def renew(self, duration: timedelta) -> bool:
        if not self.auto_renew:
            return False

        now = datetime.now(UTC)

        if self.expires_at and self.expires_at > now:
            self.expires_at += duration
        else:
            self.expires_at = now + duration

        if self.status == SubscriptionStatus.EXPIRED:
            self.status = SubscriptionStatus.ACTIVE

        return True

    def check_expiration(self) -> bool:
        if self.status == SubscriptionStatus.ACTIVE and self.expires_at:
            if datetime.now(UTC) >= self.expires_at:
                self.status = SubscriptionStatus.EXPIRED
                return True
        return False

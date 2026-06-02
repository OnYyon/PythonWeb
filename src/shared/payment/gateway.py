import asyncio
import os
from dataclasses import dataclass
from decimal import Decimal
from urllib.parse import quote
from uuid import UUID

import asyncpg
from pydantic import ValidationError

from src.payment.config import Settings
from src.payment.domain.entities.payment import CardRef, Payment, PaymentStatus
from src.payment.domain.exceptions import (
    CardNotFoundError,
    CardOwnershipError,
    InsufficientFundsError,
    PaymentDomainError,
)
from src.payment.infrastructure.repositories import (
    AsyncpgExecutor,
    PostgresCardRepository,
    PostgresPaymentRepository,
)
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class PaymentGatewayError(Exception):
    """Base error for payment gateway."""


class PaymentGatewayUnavailableError(PaymentGatewayError):
    """Raised when payment gateway is unavailable."""


def _resolve_dsn() -> str:
    try:
        settings = Settings.from_env()
        return settings.resolved_database_dsn
    except ValidationError, ValueError:
        host = os.getenv("DB_HOST", "127.0.0.1")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "cinema")
        user = os.getenv("DB_USER", "cinema")
        password = os.getenv("DB_PASSWORD", "P@ssw0rd")
        return f"postgresql://{user}:{quote(password)}@{host}:{port}/{name}"


@dataclass(frozen=True, slots=True)
class PaymentResult:
    payment_id: UUID
    status: str
    amount: Decimal


class PaymentGateway:
    def __init__(self, timeout: float | None = 5.0, dsn: str | None = None) -> None:
        self._timeout = timeout
        self._dsn = dsn or _resolve_dsn()

    def _run(self, coro):
        try:
            return asyncio.run(asyncio.wait_for(coro, timeout=self._timeout))
        except RuntimeError as exc:
            logger.error("payment_gateway_runtime_error", error=str(exc))
            raise PaymentGatewayUnavailableError(
                "payment gateway runtime error"
            ) from exc
        except TimeoutError as exc:
            logger.error("payment_gateway_timeout")
            raise PaymentGatewayUnavailableError("payment gateway timeout") from exc

    async def _pay_subscription_async(
        self, *, user_id: UUID, card_id: UUID, sub_id: UUID, amount: Decimal
    ) -> Payment:
        conn: asyncpg.Connection | None = None
        tx = None
        try:
            conn = await asyncpg.connect(dsn=self._dsn)
            tx = conn.transaction()
            await tx.start()

            executor = AsyncpgExecutor(conn)
            cards = PostgresCardRepository(executor)
            payments = PostgresPaymentRepository(executor)

            card = await cards.get_for_update(card_id)
            if card is None:
                raise CardNotFoundError(card_id)
            if card.user_id != user_id:
                raise CardOwnershipError(user_id, card_id)

            payment = Payment(
                sub_id=sub_id, amount=amount, card=CardRef.from_id(card_id)
            )

            try:
                card.debit(amount)
            except InsufficientFundsError:
                payment.mark_failed()
                await payments.create(payment)
                await tx.commit()
                return payment

            await cards.update(card)
            payment.mark_paid()
            await payments.create(payment)
            await tx.commit()
            return payment
        except PaymentDomainError:
            if tx is not None:
                await tx.rollback()
            raise
        except Exception as exc:
            if tx is not None:
                await tx.rollback()
            logger.error("payment_gateway_unavailable", error=str(exc))
            raise PaymentGatewayUnavailableError("payment gateway unavailable") from exc
        finally:
            if conn is not None:
                await conn.close()

    def pay_subscription(
        self, *, user_id: UUID, card_id: UUID, sub_id: UUID, amount: Decimal
    ) -> PaymentResult:
        payment = self._run(
            self._pay_subscription_async(
                user_id=user_id,
                card_id=card_id,
                sub_id=sub_id,
                amount=amount,
            )
        )

        status_value = (
            payment.status.value
            if isinstance(payment.status, PaymentStatus)
            else str(payment.status)
        )
        return PaymentResult(
            payment_id=payment.payment_id,
            status=status_value,
            amount=payment.amount,
        )

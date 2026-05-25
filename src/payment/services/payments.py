from decimal import Decimal
from uuid import UUID

import asyncpg

from src.payment.domain.entities.payment import CardRef, Payment
from src.payment.domain.exceptions import (
    CardNotFoundError,
    CardOwnershipError,
    InsufficientFundsError,
    PaymentNotFoundError,
)
from src.payment.infrastructure.repositories import (
    AsyncpgExecutor,
    PostgresPaymentRepository,
    PostgresUnitOfWork,
)
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class PaymentService:
    def __init__(self, *, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def pay_subscription(
        self, *, user_id: UUID, card_id: UUID, sub_id: UUID, amount: Decimal
    ) -> Payment:
        log = logger.bind(
            user_id=str(user_id),
            card_id=str(card_id),
            sub_id=str(sub_id),
            amount=str(amount),
        )
        log.info("payment_start")
        async with PostgresUnitOfWork(self._pool) as uow:
            card = await uow.cards.get_for_update(card_id)
            if card is None:
                logger.bind(card_id=str(card_id)).info("payment_card_not_found")
                raise CardNotFoundError(card_id)
            if card.user_id != user_id:
                logger.bind(user_id=str(user_id), card_id=str(card_id)).info(
                    "payment_card_forbidden"
                )
                raise CardOwnershipError(user_id, card_id)

            payment = Payment(
                sub_id=sub_id, amount=amount, card=CardRef.from_id(card_id)
            )

            try:
                card.debit(amount)
            except InsufficientFundsError:
                payment.mark_failed()
                await uow.payments.create(payment)
                logger.bind(
                    payment_id=str(payment.payment_id), reason="insufficient_funds"
                ).info("payment_failed")
                return payment

            await uow.cards.update(card)
            payment.mark_paid()
            await uow.payments.create(payment)
            logger.bind(payment_id=str(payment.payment_id)).info("payment_paid")
            return payment

    async def get_payment(self, *, payment_id: UUID) -> Payment:
        repo = PostgresPaymentRepository(AsyncpgExecutor(self._pool))
        payment = await repo.get(payment_id)
        if payment is None:
            logger.bind(payment_id=str(payment_id)).info("payment_not_found")
            raise PaymentNotFoundError(payment_id)
        return payment

    async def list_payments_for_card(self, *, card_id: UUID) -> list[Payment]:
        repo = PostgresPaymentRepository(AsyncpgExecutor(self._pool))
        payments = await repo.list_for_card(card_id)
        logger.bind(card_id=str(card_id), total=len(payments)).info(
            "payments_list_for_card"
        )
        return payments

    async def list_payments_for_subscription(self, *, sub_id: UUID) -> list[Payment]:
        repo = PostgresPaymentRepository(AsyncpgExecutor(self._pool))
        payments = await repo.list_for_subscription(sub_id)
        logger.bind(sub_id=str(sub_id), total=len(payments)).info(
            "payments_list_for_subscription"
        )
        return payments

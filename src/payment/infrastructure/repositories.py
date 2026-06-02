from collections.abc import Awaitable
from typing import Any, Protocol
from uuid import UUID

import asyncpg
from asyncpg.pool import Pool, PoolConnectionProxy
from asyncpg.transaction import Transaction

from src.payment.domain.entities.card import Card
from src.payment.domain.entities.payment import CardRef, Payment, PaymentStatus
from src.payment.domain.repositories.interfaces import (
    CardRepositoryABC,
    PaymentRepositoryABC,
    UnitOfWorkABC,
)
from src.payment.domain.utils import hash_card_id


class QueryExecutor(Protocol):
    def fetchrow(
        self, query: str, *args: Any, **kwargs: Any
    ) -> Awaitable[asyncpg.Record | None]: ...

    def fetch(
        self, query: str, *args: Any, **kwargs: Any
    ) -> Awaitable[list[asyncpg.Record]]: ...

    def execute(self, query: str, *args: Any, **kwargs: Any) -> Awaitable[str]: ...


class AsyncpgExecutor(QueryExecutor):
    def __init__(self, target: Any) -> None:
        self._target = target

    def fetchrow(
        self, query: str, *args: Any, **kwargs: Any
    ) -> Awaitable[asyncpg.Record | None]:
        return self._target.fetchrow(query, *args, **kwargs)

    def fetch(
        self, query: str, *args: Any, **kwargs: Any
    ) -> Awaitable[list[asyncpg.Record]]:
        return self._target.fetch(query, *args, **kwargs)

    def execute(self, query: str, *args: Any, **kwargs: Any) -> Awaitable[str]:
        return self._target.execute(query, *args, **kwargs)


def _card_from_row(row: asyncpg.Record) -> Card:
    return Card(card_id=row["card_id"], user_id=row["user_id"], balance=row["balance"])


def _payment_from_row(row: asyncpg.Record) -> Payment:
    return Payment(
        payment_id=row["payment_id"],
        sub_id=row["sub_id"],
        amount=row["amount"],
        card=CardRef.from_hash(row["card_hash"]),
        status=PaymentStatus(row["status"]),
        created_at=row["created_at"],
    )


class PostgresCardRepository(CardRepositoryABC):
    def __init__(self, executor: QueryExecutor) -> None:
        self._executor = executor

    async def get(self, card_id: UUID) -> Card | None:
        row = await self._executor.fetchrow(
            """
            SELECT card_id, user_id, balance
            FROM user_cards
            WHERE card_id = $1
            """,
            card_id,
        )
        return _card_from_row(row) if row else None

    async def get_for_update(self, card_id: UUID) -> Card | None:
        row = await self._executor.fetchrow(
            """
            SELECT card_id, user_id, balance
            FROM user_cards
            WHERE card_id = $1
            FOR UPDATE
            """,
            card_id,
        )
        return _card_from_row(row) if row else None

    async def list_for_user(self, user_id: UUID) -> list[Card]:
        rows = await self._executor.fetch(
            """
            SELECT card_id, user_id, balance
            FROM user_cards
            WHERE user_id = $1
            ORDER BY card_id
            """,
            user_id,
        )
        return [_card_from_row(row) for row in rows]

    async def create(self, card: Card) -> Card:
        await self._executor.execute(
            """
            INSERT INTO user_cards (card_id, user_id, balance)
            VALUES ($1, $2, $3)
            """,
            card.card_id,
            card.user_id,
            card.balance,
        )
        return card

    async def update(self, card: Card) -> Card:
        await self._executor.execute(
            """
            UPDATE user_cards
            SET balance = $1
            WHERE card_id = $2
            """,
            card.balance,
            card.card_id,
        )
        return card


class PostgresPaymentRepository(PaymentRepositoryABC):
    def __init__(self, executor: QueryExecutor) -> None:
        self._executor = executor

    async def create(self, payment: Payment) -> Payment:
        await self._executor.execute(
            """
            INSERT INTO payments (payment_id, sub_id, amount, card_hash, status, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            payment.payment_id,
            payment.sub_id,
            payment.amount,
            payment.card.card_hash,
            payment.status.value,
            payment.created_at,
        )
        return payment

    async def get(self, payment_id: UUID) -> Payment | None:
        row = await self._executor.fetchrow(
            """
            SELECT payment_id, sub_id, amount, card_hash, status, created_at
            FROM payments
            WHERE payment_id = $1
            """,
            payment_id,
        )
        return _payment_from_row(row) if row else None

    async def list_for_card(self, card_id: UUID) -> list[Payment]:
        card_hash = hash_card_id(card_id)
        rows = await self._executor.fetch(
            """
            SELECT payment_id, sub_id, amount, card_hash, status, created_at
            FROM payments
            WHERE card_hash = $1
            ORDER BY created_at DESC
            """,
            card_hash,
        )
        return [_payment_from_row(row) for row in rows]

    async def list_for_subscription(self, sub_id: UUID) -> list[Payment]:
        rows = await self._executor.fetch(
            """
            SELECT payment_id, sub_id, amount, card_hash, status, created_at
            FROM payments
            WHERE sub_id = $1
            ORDER BY created_at DESC
            """,
            sub_id,
        )
        return [_payment_from_row(row) for row in rows]


class PostgresUnitOfWork(UnitOfWorkABC):
    def __init__(self, pool: Pool) -> None:
        self._pool = pool
        self._conn: PoolConnectionProxy | None = None
        self._tx: Transaction | None = None
        self.cards: CardRepositoryABC = PostgresCardRepository(AsyncpgExecutor(pool))
        self.payments: PaymentRepositoryABC = PostgresPaymentRepository(
            AsyncpgExecutor(pool)
        )

    async def __aenter__(self) -> "PostgresUnitOfWork":
        conn = await self._pool.acquire()
        self._conn = conn
        tx = conn.transaction()
        self._tx = tx
        await tx.start()
        executor = AsyncpgExecutor(conn)
        self.cards = PostgresCardRepository(executor)
        self.payments = PostgresPaymentRepository(executor)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._tx is None or self._conn is None:
            return
        if exc_type:
            await self._tx.rollback()
        else:
            await self._tx.commit()
        await self._pool.release(self._conn)
        self._tx = None
        self._conn = None

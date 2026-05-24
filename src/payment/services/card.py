from decimal import Decimal
from uuid import UUID

import asyncpg

from src.payment.domain.entities.card import Card
from src.payment.domain.exceptions import CardNotFoundError, CardOwnershipError
from src.payment.infrastructure.repositories import (
    AsyncpgExecutor,
    PostgresCardRepository,
    PostgresUnitOfWork,
)
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class CardService:
    def __init__(self, *, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create_card(
        self, *, user_id: UUID, initial_balance: Decimal = Decimal("0.00")
    ) -> Card:
        log = logger.bind(user_id=str(user_id))
        log.info("card_create_started")
        repo = PostgresCardRepository(AsyncpgExecutor(self._pool))
        card = Card(user_id=user_id, balance=initial_balance)
        created = await repo.create(card)
        log.bind(card_id=str(created.card_id)).info("card_create_completed")
        return created

    async def get_card(self, *, card_id: UUID) -> Card:
        repo = PostgresCardRepository(AsyncpgExecutor(self._pool))
        card = await repo.get(card_id)
        if card is None:
            logger.bind(card_id=str(card_id)).info("card_get_not_found")
            raise CardNotFoundError(card_id)
        return card

    async def list_user_cards(self, *, user_id: UUID) -> list[Card]:
        repo = PostgresCardRepository(AsyncpgExecutor(self._pool))
        cards = await repo.list_for_user(user_id)
        logger.bind(user_id=str(user_id), total=len(cards)).info("cards_list")
        return cards

    async def top_up_card(
        self, *, user_id: UUID, card_id: UUID, amount: Decimal
    ) -> Card:
        async with PostgresUnitOfWork(self._pool) as uow:
            card = await uow.cards.get_for_update(card_id)
            if card is None:
                logger.bind(card_id=str(card_id)).info("card_top_up_not_found")
                raise CardNotFoundError(card_id)
            if card.user_id != user_id:
                logger.bind(user_id=str(user_id), card_id=str(card_id)).info(
                    "card_top_up_forbidden"
                )
                raise CardOwnershipError(user_id, card_id)

            card.credit(amount)
            updated = await uow.cards.update(card)
            logger.bind(card_id=str(card_id), amount=str(amount)).info(
                "card_top_up_completed"
            )
            return updated

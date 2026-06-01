import asyncpg
from fastapi import Depends, Request

from src.payment.infrastructure.db import Database
from src.payment.services.card import CardService
from src.payment.services.payments import PaymentService


def get_db(request: Request) -> Database:
    return request.app.state.db


def get_pool(db: Database = Depends(get_db)) -> "asyncpg.Pool":
    return db.pool


def get_card_service(pool=Depends(get_pool)) -> CardService:
    return CardService(pool=pool)


def get_payment_service(pool=Depends(get_pool)) -> PaymentService:
    return PaymentService(pool=pool)

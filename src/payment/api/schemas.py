from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.payment.domain.entities.payment import PaymentStatus


class CardCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    initial_balance: Decimal = Field(default=Decimal("0.00"), ge=0)


class CardTopUpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    amount: Decimal = Field(gt=0)


class CardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card_id: UUID
    user_id: UUID
    balance: Decimal


class PaymentCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    card_id: UUID
    sub_id: UUID
    amount: Decimal = Field(gt=0)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: UUID
    sub_id: UUID
    amount: Decimal
    card_hash: str
    status: PaymentStatus
    created_at: datetime

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.payment.api.deps import get_payment_service
from src.payment.api.schemas import PaymentCreateRequest, PaymentResponse
from src.payment.domain.exceptions import (
    CardNotFoundError,
    CardOwnershipError,
    InvalidAmountError,
    PaymentNotFoundError,
)
from src.payment.services.payments import PaymentService

router = APIRouter(tags=["payments"])


def _payment_response(payment) -> PaymentResponse:
    return PaymentResponse(
        payment_id=payment.payment_id,
        sub_id=payment.sub_id,
        amount=payment.amount,
        card_hash=payment.card.card_hash,
        status=payment.status,
        created_at=payment.created_at,
    )


@router.post("/payments", response_model=PaymentResponse)
async def pay_subscription(
    payload: PaymentCreateRequest,
    service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    try:
        payment = await service.pay_subscription(
            user_id=payload.user_id,
            card_id=payload.card_id,
            sub_id=payload.sub_id,
            amount=payload.amount,
        )
    except CardNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CardOwnershipError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except InvalidAmountError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _payment_response(payment)


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    try:
        payment = await service.get_payment(payment_id=payment_id)
    except PaymentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _payment_response(payment)


@router.get("/cards/{card_id}/payments", response_model=list[PaymentResponse])
async def list_payments_for_card(
    card_id: UUID,
    service: PaymentService = Depends(get_payment_service),
) -> list[PaymentResponse]:
    payments = await service.list_payments_for_card(card_id=card_id)
    return [_payment_response(payment) for payment in payments]

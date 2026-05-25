from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.payment.api.deps import get_card_service
from src.payment.api.schemas import CardCreateRequest, CardResponse, CardTopUpRequest
from src.payment.domain.exceptions import (
    CardNotFoundError,
    CardOwnershipError,
    InvalidAmountError,
)
from src.payment.services.card import CardService

router = APIRouter(tags=["cards"])


def _card_response(card) -> CardResponse:
    return CardResponse(
        card_id=card.card_id, user_id=card.user_id, balance=card.balance
    )


@router.post(
    "/cards",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_card(
    payload: CardCreateRequest,
    service: CardService = Depends(get_card_service),
) -> CardResponse:
    try:
        card = await service.create_card(
            user_id=payload.user_id, initial_balance=payload.initial_balance
        )
    except InvalidAmountError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _card_response(card)


@router.get("/cards/users/{user_id}/cards", response_model=list[CardResponse])
async def list_user_cards(
    user_id: UUID,
    service: CardService = Depends(get_card_service),
) -> list[CardResponse]:
    cards = await service.list_user_cards(user_id=user_id)
    return [_card_response(card) for card in cards]


@router.get("/cards/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: UUID,
    service: CardService = Depends(get_card_service),
) -> CardResponse:
    try:
        card = await service.get_card(card_id=card_id)
    except CardNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _card_response(card)


@router.post("/cards/{card_id}/top-up", response_model=CardResponse)
async def top_up_card(
    card_id: UUID,
    payload: CardTopUpRequest,
    service: CardService = Depends(get_card_service),
) -> CardResponse:
    try:
        card = await service.top_up_card(
            user_id=payload.user_id, card_id=card_id, amount=payload.amount
        )
    except CardNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CardOwnershipError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except InvalidAmountError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _card_response(card)

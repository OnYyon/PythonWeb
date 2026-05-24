import hashlib
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

_AMOUNT_QUANT = Decimal("0.01")


def normalize_amount(value: Decimal | int | str) -> Decimal:
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(_AMOUNT_QUANT, rounding=ROUND_HALF_UP)


def hash_card_id(card_id: UUID) -> str:
    return hashlib.sha256(card_id.bytes).hexdigest()

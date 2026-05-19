from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass
class Card:
    user_id: UUID
    card_id: UUID = uuid4()
    balance: int = 0

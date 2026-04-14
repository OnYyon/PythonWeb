from dataclasses import dataclass, field
from datetime import timedelta
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class SubPlan:
    name: str
    price: Decimal
    plan_id: UUID = field(default_factory=uuid4)
    duration: timedelta = field(default_factory=lambda: timedelta(days=30))

    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Price should be positive")

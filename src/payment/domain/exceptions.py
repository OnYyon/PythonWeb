from uuid import UUID


class PaymentDomainError(Exception):
    """Base class for payment domain errors."""


class InvalidAmountError(PaymentDomainError):
    def __init__(self, amount: object) -> None:
        super().__init__(f"Invalid amount: {amount}")


class InsufficientFundsError(PaymentDomainError):
    def __init__(self, card_id: UUID) -> None:
        super().__init__(f"Insufficient funds for card {card_id}")


class CardNotFoundError(PaymentDomainError):
    def __init__(self, card_id: UUID) -> None:
        super().__init__(f"Card {card_id} not found")


class CardOwnershipError(PaymentDomainError):
    def __init__(self, user_id: UUID, card_id: UUID) -> None:
        super().__init__(f"Card {card_id} does not belong to user {user_id}")


class PaymentNotFoundError(PaymentDomainError):
    def __init__(self, payment_id: UUID) -> None:
        super().__init__(f"Payment {payment_id} not found")

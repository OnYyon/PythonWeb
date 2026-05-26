class SubscriptionAPIErrors(Exception):
    """Base exception for subscription api"""


class NotAuth(SubscriptionAPIErrors):
    def __init__(self) -> None:
        super().__init__("Cant authenticate")

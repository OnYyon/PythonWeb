from uuid import UUID


class SubscriptionServiceError(Exception):
    """Base error for subscription service layer."""


class SubscriptionAlreadyActiveError(SubscriptionServiceError):
    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"User already has an active subscription: {user_id}")
        self.user_id = user_id


class PlanNotFoundError(SubscriptionServiceError):
    def __init__(self, plan_id: UUID) -> None:
        super().__init__(f"Plan not found: {plan_id}")
        self.plan_id = plan_id


class PlanAlreadyExistsError(SubscriptionServiceError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Plan with this name already exists: {name}")
        self.name = name


class SubscriptionNotFoundError(SubscriptionServiceError):
    def __init__(self, sub_id: UUID) -> None:
        super().__init__(f"Subscription not found: {sub_id}")
        self.sub_id = sub_id


class SubscriptionRenewalNotAllowedError(SubscriptionServiceError):
    def __init__(self, sub_id: UUID) -> None:
        super().__init__(
            f"Cannot renew this subscription (auto_renew is off): {sub_id}"
        )
        self.sub_id = sub_id

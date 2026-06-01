from decimal import Decimal
from uuid import UUID

from src.cinema_platform_django.subscription.domain.entities.subscription import (
    PaymentStatus,
    Subscription,
    SubscriptionStatus,
)
from src.cinema_platform_django.subscription.domain.repositories.interfaces import (
    PlanRepositoryABC,
    SubRepositoryABC,
)
from src.cinema_platform_django.subscription.services.exceptions import (
    PaymentCardForbiddenError,
    PaymentCardNotFoundError,
    PaymentFailedError,
    PaymentInvalidAmountError,
    PaymentServiceUnavailableError,
    PlanNotFoundError,
    SubscriptionAlreadyActiveError,
    SubscriptionNotFoundError,
    SubscriptionRenewalNotAllowedError,
    SubscriptionServiceError,
)
from src.payment.domain.exceptions import (
    CardNotFoundError,
    CardOwnershipError,
    InvalidAmountError,
)
from src.shared.payment import (
    PaymentGateway,
    PaymentGatewayUnavailableError,
    PaymentResult,
)
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class SubscriptionService:
    def __init__(
        self,
        sub_repo: SubRepositoryABC,
        plan_repo: PlanRepositoryABC,
        payment_gateway: PaymentGateway,
    ) -> None:
        self.sub_repo = sub_repo
        self.plan_repo = plan_repo
        self.payment_gateway = payment_gateway

    def _map_payment_status(self, status: str) -> PaymentStatus:
        normalized = status.lower()
        if normalized == "paid":
            return PaymentStatus.PAID
        if normalized == "failed":
            return PaymentStatus.FAILED
        return PaymentStatus.UNPAID

    def _charge_subscription(
        self, *, user_id: UUID, card_id: UUID, sub_id: UUID, amount: Decimal
    ) -> PaymentResult:
        log = logger.bind(
            user_id=str(user_id),
            card_id=str(card_id),
            sub_id=str(sub_id),
            amount=str(amount),
        )
        try:
            return self.payment_gateway.pay_subscription(
                user_id=user_id,
                card_id=card_id,
                sub_id=sub_id,
                amount=amount,
            )
        except CardNotFoundError as exc:
            log.info("payment_card_not_found")
            raise PaymentCardNotFoundError(card_id) from exc
        except CardOwnershipError as exc:
            log.info("payment_card_forbidden")
            raise PaymentCardForbiddenError(card_id) from exc
        except InvalidAmountError as exc:
            log.info("payment_request_invalid", detail=str(exc))
            raise PaymentInvalidAmountError(str(amount)) from exc
        except PaymentGatewayUnavailableError as exc:
            log.error("payment_service_unavailable", detail=str(exc))
            raise PaymentServiceUnavailableError() from exc

    def create(
        self, user_id: UUID, plan_id: UUID, auto_renew: bool = False
    ) -> Subscription:
        active_sub = self.sub_repo.get_active_for_user(user_id)
        if active_sub:
            raise SubscriptionAlreadyActiveError(user_id)

        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise PlanNotFoundError(plan_id)

        sub = Subscription(user_id, plan_id, auto_renew=auto_renew)
        return self.sub_repo.create(sub)

    def get_by_id(self, sub_id: UUID) -> Subscription:
        sub = self.sub_repo.get_by_id(sub_id)
        if not sub:
            raise SubscriptionNotFoundError(sub_id)
        return sub

    def get_active_for_user(self, user_id: UUID) -> Subscription | None:
        return self.sub_repo.get_active_for_user(user_id)

    def get_user_history(self, user_id: UUID) -> list[Subscription]:
        return self.sub_repo.list_for_user(user_id)

    def get_all(self) -> list[Subscription]:
        return self.sub_repo.get_all()

    def activate(self, sub_id: UUID) -> Subscription:
        sub = self.sub_repo.get_by_id(sub_id)
        if not sub:
            raise SubscriptionNotFoundError(sub_id)

        plan = self.plan_repo.get_by_id(sub.plan_id)
        if not plan:
            raise PlanNotFoundError(sub.plan_id)

        sub.activate(plan.duration)
        return self.sub_repo.update(sub)

    def activate_with_payment(
        self, *, user_id: UUID, sub_id: UUID, card_id: UUID
    ) -> Subscription:
        log = logger.bind(user_id=str(user_id), sub_id=str(sub_id))
        sub = self.sub_repo.get_by_id(sub_id)
        if not sub:
            raise SubscriptionNotFoundError(sub_id)

        plan = self.plan_repo.get_by_id(sub.plan_id)
        if not plan:
            raise PlanNotFoundError(sub.plan_id)

        if sub.status == SubscriptionStatus.ACTIVE:
            log.info("subscription_already_active")
            return sub
        if sub.status != SubscriptionStatus.PENDING:
            raise SubscriptionServiceError(
                f"Cannot activate subscription with status {sub.status.value}"
            )

        payment = self._charge_subscription(
            user_id=user_id,
            card_id=card_id,
            sub_id=sub.sub_id,
            amount=plan.price,
        )

        sub.transaction_id = str(payment.payment_id)
        sub.payment_status = self._map_payment_status(payment.status)

        if sub.payment_status != PaymentStatus.PAID:
            self.sub_repo.update(sub)
            raise PaymentFailedError(sub.sub_id)

        sub.activate(plan.duration)
        return self.sub_repo.update(sub)

    def cancel(self, sub_id: UUID) -> Subscription:
        sub = self.sub_repo.get_by_id(sub_id)
        if not sub:
            raise SubscriptionNotFoundError(sub_id)
        sub.cancel()
        return self.sub_repo.update(sub)

    def renew(self, sub_id: UUID) -> Subscription:
        sub = self.sub_repo.get_by_id(sub_id)
        if not sub:
            raise SubscriptionNotFoundError(sub_id)

        plan = self.plan_repo.get_by_id(sub.plan_id)
        if not plan:
            raise PlanNotFoundError(sub.plan_id)

        is_renewed = sub.renew(plan.duration)
        if not is_renewed:
            raise SubscriptionRenewalNotAllowedError(sub_id)

        sub.payment_status = PaymentStatus.PAID
        return self.sub_repo.update(sub)

    def renew_with_payment(
        self, *, user_id: UUID, sub_id: UUID, card_id: UUID
    ) -> Subscription:
        sub = self.sub_repo.get_by_id(sub_id)
        if not sub:
            raise SubscriptionNotFoundError(sub_id)

        if sub.status == SubscriptionStatus.CANCELLED:
            raise SubscriptionServiceError("Cannot renew cancelled subscription")

        if not sub.auto_renew:
            raise SubscriptionRenewalNotAllowedError(sub_id)

        plan = self.plan_repo.get_by_id(sub.plan_id)
        if not plan:
            raise PlanNotFoundError(sub.plan_id)

        payment = self._charge_subscription(
            user_id=user_id,
            card_id=card_id,
            sub_id=sub.sub_id,
            amount=plan.price,
        )

        sub.transaction_id = str(payment.payment_id)
        sub.payment_status = self._map_payment_status(payment.status)

        if sub.payment_status != PaymentStatus.PAID:
            self.sub_repo.update(sub)
            raise PaymentFailedError(sub.sub_id)

        is_renewed = sub.renew(plan.duration)
        if not is_renewed:
            raise SubscriptionRenewalNotAllowedError(sub_id)

        return self.sub_repo.update(sub)

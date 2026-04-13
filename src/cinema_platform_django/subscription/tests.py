from uuid import uuid4

from django.test import TestCase

from src.cinema_platform_django.subscription.domain.entities.subscription import (
    PaymentStatus,
    Subscription,
    SubscriptionStatus,
)
from src.cinema_platform_django.subscription.infrastructure.repository import (
    DjangoSubRepository,
)


class DjangoSubRepositoryTests(TestCase):
    def setUp(self):
        self.repo = DjangoSubRepository()
        self.user_id = uuid4()
        self.plan_id = uuid4()

    def test_can_create_and_get_subscription(self):
        sub = Subscription(user_id=self.user_id, plan_id=self.plan_id)

        self.repo.create(sub)
        fetched_sub = self.repo.get_by_id(sub.sub_id)

        self.assertIsNotNone(fetched_sub)
        assert fetched_sub is not None
        self.assertEqual(fetched_sub.sub_id, sub.sub_id)
        self.assertEqual(fetched_sub.user_id, self.user_id)
        self.assertEqual(fetched_sub.status, SubscriptionStatus.PENDING)
        self.assertEqual(fetched_sub.payment_status, PaymentStatus.UNPAID)

    def test_get_active_for_user(self):
        sub = Subscription(user_id=self.user_id, plan_id=self.plan_id)
        self.repo.create(sub)

        fetched_sub = self.repo.get_active_for_user(self.user_id)

        self.assertIsNotNone(fetched_sub)
        assert fetched_sub is not None
        self.assertEqual(fetched_sub.user_id, self.user_id)

    def test_get_by_id_returns_none_if_not_found(self):
        fetched_sub = self.repo.get_by_id(uuid4())
        self.assertIsNone(fetched_sub)

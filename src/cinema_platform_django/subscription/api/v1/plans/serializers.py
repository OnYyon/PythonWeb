from datetime import timedelta
from typing import Any

from rest_framework import serializers

from src.cinema_platform_django.subscription.domain.entities.plan import SubPlan


class PlanCreateSerializerRequestDTO(serializers.Serializer):
    """Валидирует входные данные при POST /plans/"""

    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    duration = serializers.IntegerField(
        min_value=1, required=False, default=30, help_text="Duration in days"
    )

    def validate_duration(self, value: int) -> timedelta:
        return timedelta(days=value)


class PlanSerializerDTO(serializers.Serializer):
    """Преобразует домееный датакласс SubPlan в JSON"""

    plan_id = serializers.UUIDField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    duration = serializers.IntegerField(help_text="Duration in days")

    def to_representation(self, instance: SubPlan) -> dict[str, Any]:
        return {
            "plan_id": str(instance.plan_id),
            "name": instance.name,
            "price": instance.price,
            "duration": instance.duration.days
            if hasattr(instance.duration, "days")
            else instance.duration,
        }

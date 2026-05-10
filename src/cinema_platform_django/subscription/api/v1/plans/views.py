from uuid import UUID

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from src.cinema_platform_django.subscription.api.v1.errors import make_error
from src.cinema_platform_django.subscription.api.v1.plans.serializers import (
    PlanCreateSerializerRequestDTO,
    PlanSerializerDTO,
)
from src.cinema_platform_django.subscription.dependencies import get_plan_service
from src.cinema_platform_django.subscription.services.exceptions import (
    PlanAlreadyExistsError,
    PlanNotFoundError,
)


class PublicPlanViewSet(viewsets.ViewSet):
    """GET api/v1/plans/ и GET api/v1/plans/{id}/"""

    permission_classes = [AllowAny]

    def list(self, request):
        service = get_plan_service()
        plans = service.get_all()
        return Response(PlanSerializerDTO(plans, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            plan_id = UUID(pk)
        except ValueError, TypeError:
            return make_error(status.HTTP_400_BAD_REQUEST, "invalid UUID format")

        service = get_plan_service()
        try:
            plan = service.get_by_id(plan_id)
        except PlanNotFoundError:
            return make_error(status.HTTP_404_NOT_FOUND, "plan not found")
        return Response(PlanSerializerDTO(plan).data)


class AdminPlanViewSet(viewsets.ViewSet):
    """GET/POST/PUT/DELETE /api/v1/admin/plans/"""

    def list(self, request):
        service = get_plan_service()
        plans = service.get_all()
        return Response(PlanSerializerDTO(plans, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            plan_id = UUID(pk)
        except ValueError, TypeError:
            return make_error(status.HTTP_400_BAD_REQUEST, "invalid UUID format")

        service = get_plan_service()
        try:
            plan = service.get_by_id(plan_id)
        except PlanNotFoundError:
            return make_error(status.HTTP_404_NOT_FOUND, "plan not found")
        return Response(PlanSerializerDTO(plan).data)

    def create(self, request):
        """POST api/v1/admin/plans/"""
        serializer = PlanCreateSerializerRequestDTO(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = get_plan_service()
        name = serializer.validated_data["name"]
        price = serializer.validated_data["price"]
        duration = serializer.validated_data.get("duration")
        try:
            plan = service.create(name=name, price=price, duration=duration)
        except PlanAlreadyExistsError:
            return make_error(status.HTTP_409_CONFLICT, "plan already exists")
        return Response(PlanSerializerDTO(plan).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def destroy(self, request, pk=None):
        try:
            plan_id = UUID(pk)
        except ValueError, TypeError:
            return make_error(status.HTTP_400_BAD_REQUEST, "invalid UUID format")

        service = get_plan_service()
        try:
            service.delete(plan_id)
        except PlanNotFoundError:
            return make_error(status.HTTP_409_CONFLICT, "plan already exists")
        return Response(status=status.HTTP_204_NO_CONTENT)

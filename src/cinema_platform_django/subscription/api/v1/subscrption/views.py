from uuid import UUID

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from src.cinema_platform_django.subscription.api.v1.subscrption.serializers import (
    SubscriptionCreateSerializer,
    SubscrptionSerializer,
)
from src.cinema_platform_django.subscription.dependencies import (
    get_subscription_service,
)


class SubscrptionViews(viewsets.ViewSet):
    def create(self, request) -> Response:
        """POST api/v1/subscriptions/"""
        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = get_subscription_service()
        try:
            sub = service.create(
                # TODO: use request.user.id when we will do RBAC && auth service
                user_id=request.headers.get("X-User-Id"),
                plan_id=serializer.validated_data["plan_id"],
            )
        except ValueError:
            return Response(
                {"detail": "Plan not found."}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(SubscrptionSerializer(sub).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None) -> Response:
        """GET api/v1/subscriptions/{id}"""
        try:
            sub_id = UUID(pk)
        except ValueError, TypeError:
            return Response(
                {"detail": "Invalid UUID format."}, status=status.HTTP_400_BAD_REQUEST
            )

        service = get_subscription_service()
        sub = service.get_by_id(sub_id)
        if not sub:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(SubscrptionSerializer(sub).data)

    @action(detail=False, methods=["get"])
    def me(self, request) -> Response:
        """GET api/v1/subscriptions/me/"""
        service = get_subscription_service()
        sub = service.sub_repo.get_active_for_user(request.user.id)
        print(sub)
        if not sub:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(SubscrptionSerializer(sub).data)

    @action(detail=False, methods=["get"], url_path="me/history")
    def history(self, request) -> Response:
        """GET api/v1/subscriptions/me/history"""
        service = get_subscription_service()
        subs = service.get_user_history(request.user.id)
        return Response(SubscrptionSerializer(subs, many=True).data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None) -> Response:
        """POST api/v1/subscriptions/{id}/activate"""
        service = get_subscription_service()
        try:
            sub = service.activate(UUID(pk))
            return Response(SubscrptionSerializer(sub).data)
        except ValueError, TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None) -> Response:
        """POST api/v1/subscriptions/{id}/cancel"""
        service = get_subscription_service()
        try:
            sub = service.cancel(UUID(pk))
            return Response(SubscrptionSerializer(sub).data)
        except ValueError, TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def renew(self, request) -> Response:
        """POST api/v1/subscriptions/renew (id передаем в body)"""
        sub_id = request.data.get("subscription_id")
        if not sub_id:
            return Response(
                {"detail": "subscription_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = get_subscription_service()
        try:
            sub = service.renew(UUID(sub_id))
            return Response(SubscrptionSerializer(sub).data)
        except (ValueError, TypeError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None) -> Response:
        """GET api/v1/subscriptions/{id}/status"""
        service = get_subscription_service()
        try:
            sub = service.get_by_id(UUID(pk))
        except ValueError, TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not sub:
            return Response(status=status.HTTP_404_NOT_FOUND)

        status_value = sub.status.value if hasattr(sub.status, "value") else sub.status
        return Response({"status": status_value})


class AdminSubscriptionViewSet(viewsets.ViewSet):
    """GET /api/v1/admin/subscriptions/"""

    def list(self, request) -> Response:
        service = get_subscription_service()
        subs = service.get_all()
        return Response(SubscrptionSerializer(subs, many=True).data)

    def retrieve(self, request, pk=None) -> Response:
        service = get_subscription_service()
        try:
            sub = service.get_by_id(UUID(pk))
        except ValueError, TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not sub:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(SubscrptionSerializer(sub).data)

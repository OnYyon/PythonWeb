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
    def _get_user_id(self, request) -> UUID:
        """Вспомогательный метод для получения user_id из заголовков."""
        user_id_str = request.headers.get("X-User-Id")
        if not user_id_str:
            raise ValueError("X-User-Id header is required for authentication")
        return UUID(user_id_str)

    def create(self, request) -> Response:
        """POST api/v1/subscriptions/"""
        try:
            user_id = self._get_user_id(request)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = get_subscription_service()
        try:
            sub = service.create(
                user_id=user_id,
                plan_id=serializer.validated_data["plan_id"],
                auto_renew=serializer.validated_data["auto_renew"],
            )
            print(sub)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(SubscrptionSerializer(sub).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None) -> Response:
        """GET api/v1/subscriptions/{id}"""
        try:
            user_id = self._get_user_id(request)
            sub_id = UUID(pk)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response(
                {"detail": "Invalid UUID format."}, status=status.HTTP_400_BAD_REQUEST
            )

        service = get_subscription_service()
        sub = service.get_by_id(sub_id)
        if not sub:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if str(sub.user_id) != str(user_id):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(SubscrptionSerializer(sub).data)

    @action(detail=False, methods=["get"])
    def me(self, request) -> Response:
        """GET api/v1/subscriptions/me/"""
        try:
            user_id = self._get_user_id(request)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        service = get_subscription_service()
        sub = service.sub_repo.get_active_for_user(user_id)
        if not sub:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(SubscrptionSerializer(sub).data)

    @action(detail=False, methods=["get"], url_path="me/history")
    def history(self, request) -> Response:
        """GET api/v1/subscriptions/me/history"""
        try:
            user_id = self._get_user_id(request)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        service = get_subscription_service()
        subs = service.get_user_history(user_id)
        return Response(SubscrptionSerializer(subs, many=True).data)

    @action(detail=False, methods=["post"], url_path="me/activate")
    def activate_me(self, request) -> Response:
        """POST api/v1/subscriptions/me/activate/"""
        try:
            user_id = self._get_user_id(request)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        service = get_subscription_service()
        sub = service.sub_repo.get_active_for_user(user_id)
        if not sub:
            return Response(
                {"detail": "No subscription found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            sub = service.activate(sub.sub_id)
            return Response(SubscrptionSerializer(sub).data)
        except (ValueError, TypeError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="me/cancel")
    def cancel_me(self, request) -> Response:
        """POST api/v1/subscriptions/me/cancel/"""
        try:
            user_id = self._get_user_id(request)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        service = get_subscription_service()
        sub = service.sub_repo.get_active_for_user(user_id)
        if not sub:
            return Response(
                {"detail": "No subscription found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            sub = service.cancel(sub.sub_id)
            return Response(SubscrptionSerializer(sub).data)
        except (ValueError, TypeError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="me/renew")
    def renew_me(self, request) -> Response:
        """POST api/v1/subscriptions/me/renew/"""
        try:
            user_id = self._get_user_id(request)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        service = get_subscription_service()
        sub = service.sub_repo.get_active_for_user(user_id)
        if not sub:
            return Response(
                {"detail": "No active subscription to renew"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            sub = service.renew(sub.sub_id)
            return Response(SubscrptionSerializer(sub).data)
        except (ValueError, TypeError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None) -> Response:
        """GET api/v1/subscriptions/{id}/status"""
        try:
            user_id = self._get_user_id(request)
            sub_id = UUID(pk)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response(
                {"detail": "Invalid UUID format."}, status=status.HTTP_400_BAD_REQUEST
            )

        service = get_subscription_service()
        sub = service.get_by_id(sub_id)

        if not sub:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if str(sub.user_id) != str(user_id):
            return Response(status=status.HTTP_403_FORBIDDEN)

        status_value = sub.status.value if hasattr(sub.status, "value") else sub.status
        return Response({"status": status_value})


class AdminSubscriptionViewSet(viewsets.ViewSet):
    """GET /api/v1/admin/subscriptions/"""

    def list(self) -> Response:
        service = get_subscription_service()
        subs = service.get_all()
        return Response(SubscrptionSerializer(subs, many=True).data)

    def retrieve(self, pk=None) -> Response:
        service = get_subscription_service()
        try:
            sub_id = UUID(pk)
            sub = service.get_by_id(sub_id)
        except ValueError, TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not sub:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(SubscrptionSerializer(sub).data)

    @action(detail=True, methods=["post"])
    def activate(self, pk=None) -> Response:
        """POST /api/v1/admin/subscriptions/{id}/activate/"""
        service = get_subscription_service()
        try:
            sub_id = UUID(pk)
            sub = service.activate(sub_id)
            return Response(SubscrptionSerializer(sub).data)
        except (ValueError, TypeError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancel(self, pk=None) -> Response:
        """POST /api/v1/admin/subscriptions/{id}/cancel/"""
        service = get_subscription_service()
        try:
            sub_id = UUID(pk)
            sub = service.cancel(sub_id)
            return Response(SubscrptionSerializer(sub).data)
        except (ValueError, TypeError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def renew(self, pk=None) -> Response:
        """POST /api/v1/admin/subscriptions/{id}/renew/"""
        service = get_subscription_service()
        try:
            sub_id = UUID(pk)
            sub = service.renew(sub_id)
            return Response(SubscrptionSerializer(sub).data)
        except (ValueError, TypeError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

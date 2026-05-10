from uuid import UUID

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from src.cinema_platform_django.subscription.api.v1.errors import make_error
from src.cinema_platform_django.subscription.api.v1.exceptions import (
    NotAuth,
)
from src.cinema_platform_django.subscription.api.v1.subscription.serializers import (
    SubscriptionCreateSerializer,
    SubscriptionSerializer,
)
from src.cinema_platform_django.subscription.dependencies import (
    get_subscription_service,
)
from src.cinema_platform_django.subscription.services.exceptions import (
    PlanNotFoundError,
    SubscriptionAlreadyActiveError,
    SubscriptionNotFoundError,
    SubscriptionRenewalNotAllowedError,
    SubscriptionServiceError,
)


def map_subscription_service_error(
    error: SubscriptionServiceError,
) -> Response:
    if isinstance(error, SubscriptionAlreadyActiveError):
        return make_error(
            status.HTTP_409_CONFLICT,
            "you have active subscription. use renew method",
        )
    if isinstance(error, SubscriptionRenewalNotAllowedError):
        return make_error(
            status.HTTP_409_CONFLICT,
            "cannot renew subscription (auto_renew is off)",
        )
    if isinstance(error, PlanNotFoundError):
        return make_error(status.HTTP_404_NOT_FOUND, "plan not found")
    if isinstance(error, SubscriptionNotFoundError):
        return make_error(status.HTTP_404_NOT_FOUND, "subscription not found")

    return make_error(status.HTTP_400_BAD_REQUEST, str(error))


class SubscriptionViews(viewsets.ViewSet):
    def _get_user_id(self, request) -> UUID:
        """Вспомогательный метод для получения user_id из заголовков."""
        user_id_str = request.headers.get("X-User-Id")
        if not user_id_str:
            raise NotAuth()
        return UUID(user_id_str)

    def create(self, request) -> Response:
        """POST api/v1/subscriptions/"""
        try:
            user_id = self._get_user_id(request)
        except NotAuth:
            return make_error(status.HTTP_401_UNAUTHORIZED, "neeed X-User-Id header")

        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = get_subscription_service()
        try:
            sub = service.create(
                user_id=user_id,
                plan_id=serializer.validated_data["plan_id"],
                auto_renew=serializer.validated_data["auto_renew"],
            )
        except SubscriptionServiceError as e:
            return map_subscription_service_error(e)

        return Response(
            SubscriptionSerializer(sub).data, status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, pk=None) -> Response:
        """GET api/v1/subscriptions/{id}"""
        try:
            user_id = self._get_user_id(request)
        except NotAuth:
            return make_error(status.HTTP_401_UNAUTHORIZED, "neeed X-User-Id header")

        try:
            sub_id = UUID(pk)
        except ValueError, TypeError:
            return make_error(status.HTTP_400_BAD_REQUEST, "invalid UUID format")

        service = get_subscription_service()
        try:
            sub = service.get_by_id(sub_id)
        except SubscriptionServiceError as e:
            return map_subscription_service_error(e)

        if str(sub.user_id) != str(user_id):
            return make_error(status.HTTP_403_FORBIDDEN, "ohh no, how can you do this?")

        return Response(SubscriptionSerializer(sub).data)

    @action(detail=False, methods=["get"])
    def me(self, request) -> Response:
        """GET api/v1/subscriptions/me/"""
        try:
            user_id = self._get_user_id(request)
        except NotAuth:
            return make_error(status.HTTP_401_UNAUTHORIZED, "neeed X-User-Id header")

        service = get_subscription_service()
        sub = service.get_active_for_user(user_id)
        if not sub:
            return make_error(status.HTTP_404_NOT_FOUND, "no subscription found")

        return Response(SubscriptionSerializer(sub).data)

    @action(detail=False, methods=["get"], url_path="me/history")
    def history(self, request) -> Response:
        """GET api/v1/subscriptions/me/history"""
        try:
            user_id = self._get_user_id(request)
        except NotAuth:
            return make_error(status.HTTP_401_UNAUTHORIZED, "neeed X-User-Id header")

        service = get_subscription_service()
        subs = service.get_user_history(user_id)
        return Response(SubscriptionSerializer(subs, many=True).data)

    @action(detail=False, methods=["post"], url_path="me/activate")
    def activate_me(self, request) -> Response:
        """POST api/v1/subscriptions/me/activate/"""
        try:
            user_id = self._get_user_id(request)
        except NotAuth:
            return make_error(status.HTTP_401_UNAUTHORIZED, "neeed X-User-Id header")

        service = get_subscription_service()
        sub = service.get_active_for_user(user_id)
        if not sub:
            return make_error(status.HTTP_404_NOT_FOUND, "no subscription found")

        try:
            sub = service.activate(sub.sub_id)
        except SubscriptionServiceError as e:
            return map_subscription_service_error(e)

        return Response(SubscriptionSerializer(sub).data)

    @action(detail=False, methods=["post"], url_path="me/cancel")
    def cancel_me(self, request) -> Response:
        """POST api/v1/subscriptions/me/cancel/"""
        try:
            user_id = self._get_user_id(request)
        except NotAuth:
            return make_error(status.HTTP_401_UNAUTHORIZED, "neeed X-User-Id header")

        service = get_subscription_service()
        sub = service.get_active_for_user(user_id)
        if not sub:
            return make_error(status.HTTP_404_NOT_FOUND, "no subscription found")

        try:
            sub = service.cancel(sub.sub_id)
        except SubscriptionServiceError as e:
            return map_subscription_service_error(e)

        return Response(SubscriptionSerializer(sub).data)

    @action(detail=False, methods=["post"], url_path="me/renew")
    def renew_me(self, request) -> Response:
        """POST api/v1/subscriptions/me/renew/"""
        try:
            user_id = self._get_user_id(request)
        except NotAuth:
            return make_error(status.HTTP_401_UNAUTHORIZED, "neeed X-User-Id header")

        service = get_subscription_service()
        sub = service.get_active_for_user(user_id)
        if not sub:
            return make_error(status.HTTP_404_NOT_FOUND, "no subscription found")

        try:
            sub = service.renew(sub.sub_id)
        except SubscriptionServiceError as e:
            return map_subscription_service_error(e)

        return Response(SubscriptionSerializer(sub).data)

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None) -> Response:
        """GET api/v1/subscriptions/{id}/status"""
        try:
            user_id = self._get_user_id(request)
        except NotAuth:
            return make_error(status.HTTP_401_UNAUTHORIZED, "neeed X-User-Id header")

        try:
            sub_id = UUID(pk)
        except ValueError, TypeError:
            return make_error(status.HTTP_400_BAD_REQUEST, "invalid UUID format")

        service = get_subscription_service()
        try:
            sub = service.get_by_id(sub_id)
        except SubscriptionServiceError as e:
            return map_subscription_service_error(e)

        if str(sub.user_id) != str(user_id):
            return make_error(status.HTTP_403_FORBIDDEN, "ohh no, how can you do this?")

        status_value = sub.status.value if hasattr(sub.status, "value") else sub.status
        return Response({"status": status_value})


# TODO: add check role
class AdminSubscriptionViewSet(viewsets.ViewSet):
    """GET /api/v1/admin/subscriptions/"""

    def list(self) -> Response:
        service = get_subscription_service()
        subs = service.get_all()
        return Response(SubscriptionSerializer(subs, many=True).data)

    def retrieve(self, pk=None) -> Response:
        service = get_subscription_service()
        try:
            sub_id = UUID(pk)
        except ValueError, TypeError:
            return make_error(status.HTTP_400_BAD_REQUEST, "invalid UUID format")

        try:
            sub = service.get_by_id(sub_id)
        except SubscriptionServiceError as e:
            return map_subscription_service_error(e)

        return Response(SubscriptionSerializer(sub).data)

    @action(detail=True, methods=["post"])
    def activate(self, pk=None) -> Response:
        """POST /api/v1/admin/subscriptions/{id}/activate/"""
        service = get_subscription_service()
        try:
            sub_id = UUID(pk)
        except ValueError, TypeError:
            return make_error(status.HTTP_400_BAD_REQUEST, "invalid UUID format")

        try:
            sub = service.activate(sub_id)
        except SubscriptionServiceError as e:
            return map_subscription_service_error(e)

        return Response(SubscriptionSerializer(sub).data)

    @action(detail=True, methods=["post"])
    def cancel(self, pk=None) -> Response:
        """POST /api/v1/admin/subscriptions/{id}/cancel/"""
        service = get_subscription_service()
        try:
            sub_id = UUID(pk)
        except ValueError, TypeError:
            return make_error(status.HTTP_400_BAD_REQUEST, "invalid UUID format")

        try:
            sub = service.cancel(sub_id)
        except SubscriptionServiceError as e:
            return map_subscription_service_error(e)

        return Response(SubscriptionSerializer(sub).data)

    @action(detail=True, methods=["post"])
    def renew(self, pk=None) -> Response:
        """POST /api/v1/admin/subscriptions/{id}/renew/"""
        service = get_subscription_service()
        try:
            sub_id = UUID(pk)
        except ValueError, TypeError:
            return make_error(status.HTTP_400_BAD_REQUEST, "invalid UUID format")

        try:
            sub = service.renew(sub_id)
        except SubscriptionServiceError as e:
            return map_subscription_service_error(e)

        return Response(SubscriptionSerializer(sub).data)

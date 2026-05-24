from typing import Any, cast

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from src.cinema_platform_django.user_service.api.serializers import (
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserUpdateSerializer,
)
from src.cinema_platform_django.user_service.dependencies import (
    create_user_use_case,
    delete_user_use_case,
    get_user_use_case,
    list_users_use_case,
    update_user_use_case,
)
from src.cinema_platform_django.user_service.domain.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)


def error_response(code: str, message: str, details=None, status_code=400):
    return Response(
        {
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
        status=status_code,
    )


class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        assert self.page is not None
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )


@api_view(["GET", "POST"])
def user_collection_view(request):
    if request.method == "POST":
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                code="VALIDATION_ERROR",
                message="Invalid request data",
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = create_user_use_case().execute(serializer.to_command())
        except UserAlreadyExistsError as error:
            return error_response(
                code="USER_ALREADY_EXISTS",
                message=str(error),
                details={"field": error.field},
                status_code=status.HTTP_409_CONFLICT,
            )

        return Response(
            UserDetailSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )

    users = list_users_use_case().execute()
    paginator = UserPagination()
    page = paginator.paginate_queryset(cast(Any, users), request)

    if page is None:
        list_serializer = UserListSerializer(users, many=True)
        return Response(list_serializer.data)

    list_serializer = UserListSerializer(page, many=True)
    return paginator.get_paginated_response(list_serializer.data)


@api_view(["GET", "POST", "DELETE"])
def user_detail_media_view(request, user_id):
    if request.method == "GET":
        try:
            user = get_user_use_case().execute(user_id)
        except UserNotFoundError as error:
            return error_response(
                code="USER_NOT_FOUND",
                message=str(error),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return Response(UserDetailSerializer(user).data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = UserUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                code="VALIDATION_ERROR",
                message="Invalid request data",
                details=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated_user = update_user_use_case().execute(
                user_id,
                serializer.to_command(),
            )
        except UserNotFoundError as error:
            return error_response(
                code="USER_NOT_FOUND",
                message=str(error),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except UserAlreadyExistsError as error:
            return error_response(
                code="USER_ALREADY_EXISTS",
                message=str(error),
                details={"field": error.field},
                status_code=status.HTTP_409_CONFLICT,
            )

        return Response(
            UserDetailSerializer(updated_user).data,
            status=status.HTTP_200_OK,
        )

    try:
        delete_user_use_case().execute(user_id)
    except UserNotFoundError as error:
        return error_response(
            code="USER_NOT_FOUND",
            message=str(error),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return Response(status=status.HTTP_204_NO_CONTENT)

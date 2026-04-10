from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .infrastructure.models.user import User
from .serializers import (
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserUpdateSerializer,
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
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserDetailSerializer(user).data,
                status=status.HTTP_201_CREATED,
            )
        return error_response(
            code="VALIDATION_ERROR",
            message="Invalid request data",
            details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    users = User.objects.all().order_by("-created_at")
    paginator = UserPagination()
    page = paginator.paginate_queryset(users, request)
    if page is None:
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)
    serializer = UserListSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET", "POST", "DELETE"])
def user_detail_media_view(request, user_id):
    try:
        user = User.objects.get(uuid=user_id)
    except User.DoesNotExist:
        return error_response(
            code="USER_NOT_FOUND",
            message=f"User with id={user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            return Response(
                UserDetailSerializer(updated_user).data,
                status=status.HTTP_200_OK,
            )
        return error_response(
            code="VALIDATION_ERROR",
            message="Invalid request data",
            details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

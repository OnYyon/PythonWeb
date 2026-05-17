from rest_framework import serializers

from src.cinema_platform_django.user_service.application.dto import (
    CreateUserCommand,
    UpdateUserCommand,
)


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    full_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
    )
    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
    )

    def to_command(self) -> CreateUserCommand:
        return CreateUserCommand(**self.validated_data)


class UserUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=False, min_length=6)
    full_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    def to_command(self) -> UpdateUserCommand:
        return UpdateUserCommand(**self.validated_data)


class UserListSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    username = serializers.CharField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
    phone = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class UserDetailSerializer(UserListSerializer):
    role = serializers.CharField()

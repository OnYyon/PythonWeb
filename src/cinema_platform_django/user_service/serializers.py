from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from src.cinema_platform_django.user_service.infrastructure.models.user import User


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = (
            "uuid",
            "username",
            "email",
            "password",
            "full_name",
            "phone",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("uuid", "created_at", "updated_at")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username already exists.")
        return value

    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("User with this phone already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data["password_hash"] = make_password(password)
        return User.objects.create(**validated_data)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "uuid",
            "username",
            "email",
            "full_name",
            "phone",
            "created_at",
            "updated_at",
        )


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "uuid",
            "username",
            "email",
            "full_name",
            "phone",
            "role",
            "created_at",
            "updated_at",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "full_name",
            "phone",
        )

    def validate_email(self, value):
        user = self.instance
        if user and User.objects.exclude(uuid=user.uuid).filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_username(self, value):
        user = self.instance
        if (
            user
            and User.objects.exclude(uuid=user.uuid).filter(username=value).exists()
        ):
            raise serializers.ValidationError("User with this username already exists.")
        return value

    def validate_phone(self, value):
        user = self.instance
        if (
            value
            and user
            and User.objects.exclude(uuid=user.uuid).filter(phone=value).exists()
        ):
            raise serializers.ValidationError("User with this phone already exists.")
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.password_hash = make_password(password)

        instance.save()
        return instance

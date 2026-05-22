import uuid
from django.db import models

from src.cinema_platform_django.user_service.domain.entities import UserRole


class DjangoUserRole(models.TextChoices):
    USER = UserRole.USER.value, "User"


class User(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(
        max_length=20,
        choices=DjangoUserRole.choices,
        default=UserRole.USER.value,
    )
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.role})"

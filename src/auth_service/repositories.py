from __future__ import annotations

import os
from dataclasses import dataclass

import django
from django.contrib.auth.hashers import check_password
from django.db import connection
from django.db.utils import IntegrityError

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "src.cinema_platform_django.config.settings"
)
django.setup()


@dataclass(slots=True)
class User:
    id: str
    username: str
    full_name: str
    role: str


@dataclass(slots=True)
class Role:
    id: int
    name: str


class AuthRepository:
    def __init__(self) -> None:
        self._ensure_tables()
        self._bootstrap_default_roles()

    def get_user_by_credentials(self, username: str, password: str) -> User | None:
        from src.cinema_platform_django.user_service.infrastructure.models.user import (
            User as DjangoUser,
        )

        user = DjangoUser.objects.filter(username=username).first()
        if user is None or not check_password(password, user.password_hash):
            return None
        return User(
            id=str(user.uuid),
            username=user.username,
            full_name=user.full_name,
            role=user.role,
        )

    def is_token_revoked(self, jti: str) -> bool:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM auth_revoked_tokens WHERE jti = %s LIMIT 1", [jti]
            )
            return cursor.fetchone() is not None

    def revoke_token(self, jti: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO auth_revoked_tokens (jti) VALUES (%s) ON CONFLICT (jti) DO NOTHING",
                [jti],
            )

    def create_role(self, name: str) -> Role:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO auth_roles (name) VALUES (%s) RETURNING id, name",
                    [name],
                )
                role_id, role_name = cursor.fetchone()
        except IntegrityError as exc:
            raise ValueError("role already exists") from exc
        return Role(id=role_id, name=role_name)

    def get_role(self, role_id: int) -> Role | None:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM auth_roles WHERE id = %s", [role_id])
            row = cursor.fetchone()
        if row is None:
            return None
        return Role(id=row[0], name=row[1])

    def delete_role(self, role_id: int) -> bool:
        from src.cinema_platform_django.user_service.infrastructure.models.user import (
            User as DjangoUser,
        )

        role = self.get_role(role_id=role_id)
        if role is None:
            return False

        if DjangoUser.objects.filter(role=role.name).exists():
            return False

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM auth_roles WHERE id = %s", [role_id])
            return cursor.rowcount > 0

    def get_users_by_role(
        self, role_id: int, page: int, limit: int
    ) -> tuple[list[User], int]:
        from src.cinema_platform_django.user_service.infrastructure.models.user import (
            User as DjangoUser,
        )

        role = self.get_role(role_id=role_id)
        if role is None:
            return [], 0
        queryset = DjangoUser.objects.filter(role=role.name).order_by("created_at")
        total = queryset.count()
        start = (page - 1) * limit
        rows = queryset[start : start + limit]
        items = [
            User(
                id=str(user.uuid),
                username=user.username,
                full_name=user.full_name,
                role=user.role,
            )
            for user in rows
        ]
        return items, total

    def _ensure_tables(self) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_roles (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(64) UNIQUE NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_revoked_tokens (
                    jti VARCHAR(64) PRIMARY KEY,
                    revoked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )

    def _bootstrap_default_roles(self) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO auth_roles (name)
                VALUES ('admin'), ('user')
                ON CONFLICT (name) DO NOTHING
                """
            )

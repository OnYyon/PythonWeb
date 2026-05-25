from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status

from src.auth_service.repositories import AuthRepository, Role
from src.shared.auth_token import JwtTokenManager, TokenError


class AuthService:
    def __init__(self, repository: AuthRepository, token_manager: JwtTokenManager) -> None:
        self.repository = repository
        self.token_manager = token_manager

    def login(self, username: str, password: str) -> dict[str, str]:
        user = self.repository.get_user_by_credentials(username=username, password=password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

        claims = {
            "sub": str(user.id),
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
        }
        access_token = self.token_manager.create_access_token(claims)
        refresh_token = self.token_manager.create_refresh_token(claims)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "full_name": user.full_name,
        }

    def refresh(self, refresh_token: str) -> dict[str, str]:
        payload = self._parse_token(refresh_token, expected_type="refresh")
        access_claims = {
            "sub": payload["sub"],
            "username": payload["username"],
            "full_name": payload["full_name"],
            "role": payload["role"],
        }
        access_token = self.token_manager.create_access_token(access_claims)
        new_refresh = self.token_manager.create_refresh_token(access_claims)
        return {
            "access_token": access_token,
            "refresh_token": new_refresh,
            "full_name": payload["full_name"],
        }

    def validate(self, token: str) -> None:
        self._parse_token(token, expected_type="access")

    def parse_access_token(self, token: str) -> dict[str, Any]:
        return self._parse_token(token, expected_type="access")

    def logout(self, token: str) -> None:
        payload = self._parse_token(token, expected_type=None)
        self.repository.revoke_token(payload["jti"])

    def _parse_token(self, token: str, expected_type: str | None) -> dict[str, Any]:
        try:
            payload = self.token_manager.parse_and_validate(token)
        except TokenError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token") from exc

        token_type = payload.get("token_type")
        if expected_type and token_type != expected_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="wrong token type")

        jti = payload.get("jti")
        if not isinstance(jti, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token payload")
        if self.repository.is_token_revoked(jti):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token revoked")
        return payload


class RoleService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    def create_role(self, name: str) -> Role:
        try:
            return self.repository.create_role(name=name)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    def get_users_by_role(self, role_id: int, page: int, limit: int) -> dict[str, Any]:
        role = self.repository.get_role(role_id=role_id)
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="role not found")
        items, total = self.repository.get_users_by_role(role_id=role_id, page=page, limit=limit)
        return {
            "role_id": role.id,
            "role_name": role.name,
            "page": page,
            "limit": limit,
            "total": total,
            "items": [
                {
                    "user_id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                }
                for user in items
            ],
        }

    def delete_role(self, role_id: int) -> None:
        role = self.repository.get_role(role_id=role_id)
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="role not found")
        deleted = self.repository.delete_role(role_id=role_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="role has assigned users or cannot be deleted",
            )

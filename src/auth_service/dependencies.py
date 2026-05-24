from __future__ import annotations

from functools import lru_cache

from src.auth_service.repositories import AuthRepository
from src.auth_service.services import AuthService, RoleService
from src.shared.auth_token import JwtTokenManager


@lru_cache
def get_repository() -> AuthRepository:
    return AuthRepository()


@lru_cache
def get_token_manager() -> JwtTokenManager:
    return JwtTokenManager()


def get_auth_service() -> AuthService:
    return AuthService(repository=get_repository(), token_manager=get_token_manager())


def get_role_service() -> RoleService:
    return RoleService(repository=get_repository())


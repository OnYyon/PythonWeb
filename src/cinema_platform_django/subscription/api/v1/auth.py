from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from src.cinema_platform_django.subscription.api.v1.exceptions import NotAuth
from src.shared.auth_token import JwtTokenManager, TokenError


@dataclass(frozen=True, slots=True)
class AuthContext:
    user_id: UUID
    role: str


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        return ""
    parts = authorization.split(" ", maxsplit=1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return authorization.strip()


def get_auth_context(request) -> AuthContext:
    token = _extract_bearer_token(request.headers.get("Authorization"))
    if not token:
        raise NotAuth()

    try:
        payload = JwtTokenManager().parse_and_validate(token)
    except TokenError as exc:
        raise NotAuth() from exc

    if payload.get("token_type") != "access":
        raise NotAuth()

    sub = payload.get("sub")
    if not sub:
        raise NotAuth()

    try:
        user_id = UUID(str(sub))
    except ValueError as exc:
        raise NotAuth() from exc

    role = str(payload.get("role", ""))
    return AuthContext(user_id=user_id, role=role)

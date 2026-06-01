from dataclasses import dataclass
from uuid import UUID

from fastapi import Header, HTTPException, status

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


def get_auth_context(authorization: str | None = Header(None)) -> AuthContext:
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authorization token required",
        )

    try:
        payload = JwtTokenManager().parse_and_validate(token)
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        ) from exc

    if payload.get("token_type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token type"
        )

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token payload"
        )

    try:
        user_id = UUID(str(sub))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token payload"
        ) from exc

    role = str(payload.get("role", ""))
    return AuthContext(user_id=user_id, role=role)

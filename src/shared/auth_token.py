import os
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
from jwt import InvalidTokenError


class TokenError(Exception):
    """Raised when token cannot be validated or parsed."""


class JwtTokenManager:
    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str | None = None,
        access_minutes: int | None = None,
        refresh_days: int | None = None,
    ) -> None:
        self.secret_key = secret_key or os.getenv("AUTH_SECRET_KEY")
        if not self.secret_key:
            raise ValueError("AUTH_SECRET_KEY must be set")
        if len(self.secret_key) < 32:
            raise ValueError("AUTH_SECRET_KEY must be at least 32 characters long")
        self.algorithm = algorithm or os.getenv("AUTH_ALGORITHM", "HS256")
        self.access_minutes = access_minutes or int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )
        self.refresh_days = refresh_days or int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "14")
        )

    def create_access_token(self, claims: dict[str, Any]) -> str:
        return self._encode(
            claims=claims,
            token_type="access",
            expires=timedelta(minutes=self.access_minutes),
        )

    def create_refresh_token(self, claims: dict[str, Any]) -> str:
        return self._encode(
            claims=claims,
            token_type="refresh",
            expires=timedelta(days=self.refresh_days),
        )

    def parse_and_validate(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except InvalidTokenError as exc:
            raise TokenError("invalid token") from exc
        return payload

    def _encode(
        self, claims: dict[str, Any], token_type: str, expires: timedelta
    ) -> str:
        now = datetime.now(timezone.utc)
        payload = claims.copy()
        payload.update(
            {
                "jti": str(uuid4()),
                "iat": int(now.timestamp()),
                "exp": int((now + expires).timestamp()),
                "token_type": token_type,
            }
        )
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

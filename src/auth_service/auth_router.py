from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response, status

from src.auth_service.dependencies import get_auth_service
from src.auth_service.schemas import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenPairResponse,
)
from src.auth_service.services import AuthService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        return ""
    parts = authorization.split(" ", maxsplit=1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return ""


@router.post("/login", response_model=TokenPairResponse)
def login(
    payload: LoginRequest, service: Annotated[AuthService, Depends(get_auth_service)]
) -> TokenPairResponse:
    logger.info("auth.login requested username=%s", payload.username)
    tokens = service.login(username=payload.username, password=payload.password)
    logger.info("auth.login succeeded username=%s", payload.username)
    return TokenPairResponse(**tokens)


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(
    payload: RefreshRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenPairResponse:
    logger.info("auth.refresh requested")
    tokens = service.refresh(refresh_token=payload.refresh_token)
    logger.info("auth.refresh succeeded")
    return TokenPairResponse(**tokens)


@router.get("/validate", status_code=status.HTTP_204_NO_CONTENT)
def validate(
    service: Annotated[AuthService, Depends(get_auth_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> Response:
    token = _extract_bearer_token(authorization)
    service.validate(token=token)
    logger.info("auth.validate succeeded")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: LogoutRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Response:
    service.logout(payload.token)
    logger.info("auth.logout token revoked")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

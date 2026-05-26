from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth_service.dependencies import get_auth_service, get_role_service
from src.auth_service.schemas import CreateRoleRequest, RoleResponse, RoleUsersResponse
from src.auth_service.services import AuthService, RoleService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/role", tags=["role"])
bearer_scheme = HTTPBearer(auto_error=False)


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        return ""
    parts = authorization.split(" ", maxsplit=1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return ""


def _require_admin(
    service: Annotated[AuthService, Depends(get_auth_service)],
    creds: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
) -> None:
    token = creds.credentials if creds else ""
    payload = service.parse_access_token(token=token)
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="admin access required"
        )


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: CreateRoleRequest,
    service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[None, Depends(_require_admin)],
) -> RoleResponse:
    role = service.create_role(name=payload.name)
    logger.info("role.created id=%s name=%s", role.id, role.name)
    return RoleResponse(id=role.id, name=role.name)


@router.get("/{role_id}", response_model=RoleUsersResponse)
def get_role_users(
    role_id: int,
    service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[None, Depends(_require_admin)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> RoleUsersResponse:
    data = service.get_users_by_role(role_id=role_id, page=page, limit=limit)
    logger.info("role.users role_id=%s page=%s limit=%s", role_id, page, limit)
    return RoleUsersResponse(**data)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[None, Depends(_require_admin)],
) -> Response:
    service.delete_role(role_id=role_id)
    logger.info("role.deleted role_id=%s", role_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    token: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    full_name: str


class CreateRoleRequest(BaseModel):
    name: str = Field(min_length=2, max_length=64)


class RoleResponse(BaseModel):
    id: int
    name: str


class RoleUserItem(BaseModel):
    user_id: int
    username: str
    full_name: str


class RoleUsersResponse(BaseModel):
    role_id: int
    role_name: str
    page: int
    limit: int
    total: int
    items: list[RoleUserItem]

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.api.deps import get_admin_service, get_current_admin
from src.schemas.user import UserActiveUpdate, UserProfile, UserRoleUpdate
from src.service.admin import AdminService

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/users")
async def list_users(
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[UserProfile]:
    return await admin_service.get_all_users(limit, offset)


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
) -> UserProfile:
    return await admin_service.get_user(user_id)


@router.patch("/users/{user_id}/role")
async def set_user_role(
    user_id: int,
    body: UserRoleUpdate,
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
) -> UserProfile:
    return await admin_service.set_role(user_id, body.role.value)


@router.patch("/users/{user_id}/active")
async def set_user_active(
    user_id: int,
    body: UserActiveUpdate,
    admin_service: Annotated[AdminService, Depends(get_admin_service)],
) -> UserProfile:
    return await admin_service.set_active(user_id, body.is_active)

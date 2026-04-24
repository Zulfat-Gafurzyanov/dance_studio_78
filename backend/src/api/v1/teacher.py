from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.deps import get_current_admin, get_teacher_service
from src.schemas.teacher import (
    TeacherCreate,
    TeacherPhotoCreate,
    TeacherPhotoResponse,
    TeacherPhotoUpdate,
    TeacherReorderItem,
    TeacherResponse,
    TeacherUpdate,
)
from src.service.teacher import TeacherService

router = APIRouter(prefix="/teachers", tags=["teachers"])


@router.get("")
async def get_all(
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> list[TeacherResponse]:
    return await teacher_service.get_all()


@router.post(
    "/reorder",
    dependencies=[Depends(get_current_admin)],
    status_code=204
)
async def reorder(
    body: list[TeacherReorderItem],
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> None:
    await teacher_service.reorder(body)


@router.get("/{teacher_id}")
async def get_by_id(
    teacher_id: int,
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> TeacherResponse:
    return await teacher_service.get_by_id(teacher_id)


@router.post(
    "",
    dependencies=[Depends(get_current_admin)],
    status_code=201
)
async def create(
    body: TeacherCreate,
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> TeacherResponse:
    return await teacher_service.create(body)


@router.patch(
    "/{teacher_id}",
    dependencies=[Depends(get_current_admin)]
)
async def update(
    teacher_id: int,
    body: TeacherUpdate,
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> TeacherResponse:
    return await teacher_service.update(teacher_id, body)


@router.delete(
    "/{teacher_id}",
    dependencies=[Depends(get_current_admin)],
    status_code=204
)
async def delete(
    teacher_id: int,
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> None:
    await teacher_service.delete(teacher_id)


# ===== Photo =====

@router.post(
    "/{teacher_id}/photos",
    dependencies=[Depends(get_current_admin)],
    status_code=201
)
async def add_photo(
    teacher_id: int,
    body: TeacherPhotoCreate,
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> TeacherPhotoResponse:
    return await teacher_service.add_photo(teacher_id, body)


@router.patch(
    "/photos/{photo_id}",
    dependencies=[Depends(get_current_admin)],
)
async def update_photo(
    photo_id: int,
    body: TeacherPhotoUpdate,
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> TeacherPhotoResponse:
    return await teacher_service.update_photo(photo_id, body)


@router.delete(
    "/photos/{photo_id}",
    dependencies=[Depends(get_current_admin)],
    status_code=204
)
async def delete_photo(
    photo_id: int,
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)],
) -> None:
    await teacher_service.delete_photo(photo_id)

from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.deps import get_current_admin, get_style_service
from src.schemas.style import (
    StyleCreate,
    StyleImageCreate,
    StyleImageResponse,
    StyleImageUpdate,
    StyleResponse,
    StyleUpdate,
)
from src.service.style import StyleService

router = APIRouter(prefix="/styles", tags=["styles"])


@router.get("")
async def get_all(
    style_service: Annotated[StyleService, Depends(get_style_service)],
) -> list[StyleResponse]:
    return await style_service.get_all()


@router.get("/{style_id}")
async def get_by_id(
    style_id: int,
    style_service: Annotated[StyleService, Depends(get_style_service)],
) -> StyleResponse:
    return await style_service.get_by_id(style_id)


@router.post(
    "",
    dependencies=[Depends(get_current_admin)],
    status_code=201
)
async def create(
    body: StyleCreate,
    style_service: Annotated[StyleService, Depends(get_style_service)],
) -> StyleResponse:
    return await style_service.create(body)


@router.patch(
    "/{style_id}",
    dependencies=[Depends(get_current_admin)]
)
async def update(
    style_id: int,
    body: StyleUpdate,
    style_service: Annotated[StyleService, Depends(get_style_service)],
) -> StyleResponse:
    return await style_service.update(style_id, body)


@router.delete(
    "/{style_id}",
    dependencies=[Depends(get_current_admin)],
    status_code=204
    )
async def delete(
    style_id: int,
    style_service: Annotated[StyleService, Depends(get_style_service)],
) -> None:
    await style_service.delete(style_id)


# ===== Image =====

@router.post(
    "/{style_id}/images",
    dependencies=[Depends(get_current_admin)],
    status_code=201
)
async def add_image(
    style_id: int,
    body: StyleImageCreate,
    style_service: Annotated[StyleService, Depends(get_style_service)],
) -> StyleImageResponse:
    return await style_service.add_image(style_id, body)


@router.patch(
    "/images/{image_id}",
    dependencies=[Depends(get_current_admin)],
)
async def update_image(
    image_id: int,
    body: StyleImageUpdate,
    style_service: Annotated[StyleService, Depends(get_style_service)],
) -> StyleImageResponse:
    return await style_service.update_image(image_id, body)


@router.delete(
    "/images/{image_id}",
    dependencies=[Depends(get_current_admin)],
    status_code=204
)
async def delete_image(
    image_id: int,
    style_service: Annotated[StyleService, Depends(get_style_service)],
) -> None:
    await style_service.delete_image(image_id)

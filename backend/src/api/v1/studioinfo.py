from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.deps import get_current_admin, get_studioinfo_service
from src.schemas.studioinfo import StudioInfoResponse, StudioInfoUpdate
from src.service.studioinfo import StudioInfoService

router = APIRouter(prefix="/studio-info", tags=["studio-info"])


@router.get("", response_model=StudioInfoResponse)
async def get_studio_info(
    service: Annotated[StudioInfoService, Depends(get_studioinfo_service)],
) -> StudioInfoResponse:
    return await service.get()


@router.patch(
    "",
    response_model=StudioInfoResponse,
    dependencies=[Depends(get_current_admin)],
)
async def update_studio_info(
    body: StudioInfoUpdate,
    service: Annotated[StudioInfoService, Depends(get_studioinfo_service)],
) -> StudioInfoResponse:
    return await service.update(body)

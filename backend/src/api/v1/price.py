from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.deps import get_current_admin, get_price_service
from src.schemas.price import (
    PricePlanCreate,
    PricePlanOptionCreate,
    PricePlanOptionResponse,
    PricePlanOptionUpdate,
    PricePlanResponse,
    PricePlanUpdate,
)
from src.service.price import PriceService

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("")
async def get_all(
    service: Annotated[PriceService, Depends(get_price_service)],
) -> list[PricePlanResponse]:
    return await service.get_all()


@router.get("/{plan_id}")
async def get_by_id(
    plan_id: int,
    service: Annotated[PriceService, Depends(get_price_service)],
) -> PricePlanResponse:
    return await service.get_by_id(plan_id)


@router.post("", dependencies=[Depends(get_current_admin)], status_code=201)
async def create(
    body: PricePlanCreate,
    service: Annotated[PriceService, Depends(get_price_service)],
) -> PricePlanResponse:
    return await service.create(body)


@router.patch("/{plan_id}", dependencies=[Depends(get_current_admin)])
async def update(
    plan_id: int,
    body: PricePlanUpdate,
    service: Annotated[PriceService, Depends(get_price_service)],
) -> PricePlanResponse:
    return await service.update(plan_id, body)


@router.delete(
    "/{plan_id}", dependencies=[Depends(get_current_admin)], status_code=204
)
async def delete(
    plan_id: int,
    service: Annotated[PriceService, Depends(get_price_service)],
) -> None:
    await service.delete(plan_id)


# ===== Option =====

@router.post(
    "/{plan_id}/options",
    dependencies=[Depends(get_current_admin)],
    status_code=201,
)
async def add_option(
    plan_id: int,
    body: PricePlanOptionCreate,
    service: Annotated[PriceService, Depends(get_price_service)],
) -> PricePlanOptionResponse:
    return await service.add_option(plan_id, body)


@router.patch(
    "/options/{option_id}", dependencies=[Depends(get_current_admin)]
)
async def update_option(
    option_id: int,
    body: PricePlanOptionUpdate,
    service: Annotated[PriceService, Depends(get_price_service)],
) -> PricePlanOptionResponse:
    return await service.update_option(option_id, body)


@router.delete(
    "/options/{option_id}",
    dependencies=[Depends(get_current_admin)],
    status_code=204,
)
async def delete_option(
    option_id: int,
    service: Annotated[PriceService, Depends(get_price_service)],
) -> None:
    await service.delete_option(option_id)

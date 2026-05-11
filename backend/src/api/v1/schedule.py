import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.api.deps import get_current_admin, get_current_user_id, get_schedule_service
from src.schemas.schedule import (
    EnrollmentResponse,
    EventCreate,
    EventResponse,
    EventUpdate,
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
)
from src.service.schedule import ScheduleService

router = APIRouter(prefix="/schedule", tags=["schedule"])


# ===== Templates (admin) =====

@router.get("/templates", dependencies=[Depends(get_current_admin)])
async def get_templates(
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> list[TemplateResponse]:
    return await service.get_all_templates()


@router.post("/templates", dependencies=[Depends(get_current_admin)], status_code=201)
async def create_template(
    body: TemplateCreate,
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> TemplateResponse:
    return await service.create_template(body)


@router.patch("/templates/{template_id}", dependencies=[Depends(get_current_admin)])
async def update_template(
    template_id: int,
    body: TemplateUpdate,
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> TemplateResponse:
    return await service.update_template(template_id, body)


@router.delete("/templates/{template_id}", dependencies=[Depends(get_current_admin)], status_code=204)
async def delete_template(
    template_id: int,
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> None:
    await service.delete_template(template_id)


# ===== Events =====

@router.get("/events/admin", dependencies=[Depends(get_current_admin)])
async def get_events_admin(
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
    date_from: datetime.date = Query(...),
    date_to: datetime.date = Query(...),
) -> list[EventResponse]:
    return await service.get_events_admin(date_from, date_to)


@router.get("/events")
async def get_events(
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
    date_from: datetime.date = Query(...),
    date_to: datetime.date = Query(...),
) -> list[EventResponse]:
    return await service.get_events(date_from, date_to)


@router.get("/events/{event_id}")
async def get_event(
    event_id: int,
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> EventResponse:
    return await service.get_event_by_id(event_id)


@router.post("/events", dependencies=[Depends(get_current_admin)], status_code=201)
async def create_event(
    body: EventCreate,
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> EventResponse:
    return await service.create_event(body)


@router.patch("/events/{event_id}", dependencies=[Depends(get_current_admin)])
async def update_event(
    event_id: int,
    body: EventUpdate,
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> EventResponse:
    return await service.update_event(event_id, body)


@router.delete("/events/{event_id}", dependencies=[Depends(get_current_admin)], status_code=204)
async def delete_event(
    event_id: int,
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> None:
    await service.delete_event(event_id)


# ===== Enrollment =====

@router.get("/my-enrollments")
async def get_my_enrollments(
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> list[int]:
    return await service.get_my_enrollments(user_id)

@router.post("/events/{event_id}/enroll", status_code=201)
async def enroll(
    event_id: int,
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> EnrollmentResponse:
    return await service.enroll(event_id, user_id)


@router.delete("/events/{event_id}/enroll", status_code=204)
async def cancel_enrollment(
    event_id: int,
    service: Annotated[ScheduleService, Depends(get_schedule_service)],
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> None:
    await service.cancel_enrollment(event_id, user_id)

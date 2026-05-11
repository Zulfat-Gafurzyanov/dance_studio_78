import datetime

from fastapi import HTTPException, status

from src.core.constants import BOOKING_HORIZON_DAYS
from pg.models.schedule import EventStatus
from src.repository.schedule import ScheduleRepository
from src.schemas.schedule import (
    EnrollmentResponse,
    EventCreate,
    EventResponse,
    EventUpdate,
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
)


class ScheduleService:
    def __init__(self, repository: ScheduleRepository):
        self.repository = repository

    def _map_template(self, row) -> TemplateResponse:
        return TemplateResponse(
            id=row["id"],
            style_id=row["style_id"],
            style_name=row["style_name"],
            teacher_id=row["teacher_id"],
            teacher_name=row["teacher_name"],
            day_of_week=row["day_of_week"],
            time_start=row["time_start"],
            duration_minutes=row["duration_minutes"],
            max_students=row["max_students"],
            is_active=row["is_active"],
        )

    def _map_event(self, row) -> EventResponse:
        return EventResponse(
            id=row["id"],
            template_id=row["template_id"],
            style_id=row["style_id"],
            style_name=row["style_name"],
            teacher_id=row["teacher_id"],
            teacher_name=row["teacher_name"],
            substitute_teacher_id=row["substitute_teacher_id"],
            substitute_teacher_name=row["substitute_teacher_name"],
            event_date=row["event_date"],
            time_start=row["time_start"],
            duration_minutes=row["duration_minutes"],
            max_students=row["max_students"],
            status=row["status"],
            enrolled_count=row["enrolled_count"],
        )

    # ===== Templates =====

    async def get_all_templates(self) -> list[TemplateResponse]:
        rows = await self.repository.get_all_templates()
        return [self._map_template(r) for r in rows]

    async def get_template_by_id(self, template_id: int) -> TemplateResponse:
        row = await self.repository.get_template_by_id(template_id)
        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Шаблон не найден")
        return self._map_template(row)

    async def create_template(self, data: TemplateCreate) -> TemplateResponse:
        record = await self.repository.create_template(
            style_id=data.style_id,
            teacher_id=data.teacher_id,
            day_of_week=data.day_of_week,
            time_start=data.time_start,
            duration_minutes=data.duration_minutes,
            max_students=data.max_students,
        )
        if not record:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Ошибка создания шаблона")
        row = await self.repository.get_template_by_id(record["id"])
        return self._map_template(row)

    async def update_template(self, template_id: int, data: TemplateUpdate) -> TemplateResponse:
        row = await self.repository.get_template_by_id(template_id)
        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Шаблон не найден")
        await self.repository.update_template(template_id, data.model_dump(exclude_unset=True))
        row = await self.repository.get_template_by_id(template_id)
        return self._map_template(row)

    async def delete_template(self, template_id: int) -> None:
        row = await self.repository.get_template_by_id(template_id)
        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Шаблон не найден")
        await self.repository.delete_template(template_id)

    # ===== Events =====

    async def get_events(
        self, date_from: datetime.date, date_to: datetime.date
    ) -> list[EventResponse]:
        today = datetime.date.today()
        horizon = today + datetime.timedelta(days=BOOKING_HORIZON_DAYS)
        if date_from > date_to:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "date_from не может быть позже date_to")
        if date_to > horizon:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Диапазон дат не может превышать {BOOKING_HORIZON_DAYS} дней вперёд"
            )
        rows = await self.repository.get_events_by_date_range(date_from, date_to)
        return [self._map_event(r) for r in rows]

    async def get_events_admin(
        self, date_from: datetime.date, date_to: datetime.date
    ) -> list[EventResponse]:
        if date_from > date_to:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "date_from не может быть позже date_to")
        rows = await self.repository.get_events_by_date_range(date_from, date_to)
        return [self._map_event(r) for r in rows]

    async def get_event_by_id(self, event_id: int) -> EventResponse:
        row = await self.repository.get_event_by_id(event_id)
        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Занятие не найдено")
        return self._map_event(row)

    async def create_event(self, data: EventCreate) -> EventResponse:
        record = await self.repository.create_event(
            style_id=data.style_id,
            teacher_id=data.teacher_id,
            event_date=data.event_date,
            time_start=data.time_start,
            duration_minutes=data.duration_minutes,
            max_students=data.max_students,
            template_id=data.template_id,
        )
        if not record:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Ошибка создания занятия")
        row = await self.repository.get_event_by_id(record["id"])
        return self._map_event(row)

    async def update_event(self, event_id: int, data: EventUpdate) -> EventResponse:
        row = await self.repository.get_event_by_id(event_id)
        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Занятие не найдено")
        await self.repository.update_event(event_id, data.model_dump(exclude_unset=True))
        row = await self.repository.get_event_by_id(event_id)
        return self._map_event(row)

    async def delete_event(self, event_id: int) -> None:
        row = await self.repository.get_event_by_id(event_id)
        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Занятие не найдено")
        await self.repository.delete_event(event_id)

    # ===== Enrollment =====

    async def get_my_enrollments(self, user_id: int) -> list[int]:
        return await self.repository.get_user_enrolled_event_ids(user_id)

    async def enroll(self, event_id: int, user_id: int) -> EnrollmentResponse:
        row = await self.repository.get_event_by_id(event_id)
        if not row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Занятие не найдено")
        if row["status"] != EventStatus.SCHEDULED.value:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Занятие отменено")
        today = datetime.date.today()
        if row["event_date"] < today:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нельзя записаться на прошедшее занятие")
        if row["event_date"] > today + datetime.timedelta(days=BOOKING_HORIZON_DAYS):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Занятие вне горизонта записи")
        if row["enrolled_count"] >= row["max_students"]:
            raise HTTPException(status.HTTP_409_CONFLICT, "Занятие заполнено")
        existing = await self.repository.get_user_enrollment(event_id, user_id)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "Вы уже записаны на это занятие")
        record = await self.repository.enroll(event_id, user_id)
        return EnrollmentResponse(
            id=record["id"],
            event_id=record["event_id"],
            user_id=record["user_id"],
        )

    async def cancel_enrollment(self, event_id: int, user_id: int) -> None:
        existing = await self.repository.get_user_enrollment(event_id, user_id)
        if not existing:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Запись не найдена")
        await self.repository.cancel_enrollment(event_id, user_id)

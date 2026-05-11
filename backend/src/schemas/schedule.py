import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TemplateCreate(BaseModel):
    style_id: int
    teacher_id: int
    day_of_week: int = Field(ge=0, le=6)
    time_start: datetime.time
    duration_minutes: int = Field(default=60, ge=15, le=240)
    max_students: int = Field(default=8, ge=1, le=50)


class TemplateUpdate(BaseModel):
    style_id: int | None = None
    teacher_id: int | None = None
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    time_start: datetime.time | None = None
    duration_minutes: int | None = Field(default=None, ge=15, le=240)
    max_students: int | None = Field(default=None, ge=1, le=50)
    is_active: bool | None = None

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "TemplateUpdate":
        if not self.model_fields_set:
            raise ValueError("Необходимо указать хотя бы одно поле")
        return self


class TemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    style_id: int
    style_name: str
    teacher_id: int
    teacher_name: str
    day_of_week: int
    time_start: datetime.time
    duration_minutes: int
    max_students: int
    is_active: bool


class EventCreate(BaseModel):
    style_id: int
    teacher_id: int
    event_date: datetime.date
    time_start: datetime.time
    duration_minutes: int = Field(default=60, ge=15, le=240)
    max_students: int = Field(default=8, ge=1, le=50)
    template_id: int | None = None


class EventUpdate(BaseModel):
    substitute_teacher_id: int | None = None
    status: Literal["запланировано", "отменено"] | None = None
    max_students: int | None = Field(default=None, ge=1, le=50)
    time_start: datetime.time | None = None
    duration_minutes: int | None = Field(default=None, ge=15, le=240)

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "EventUpdate":
        if not self.model_fields_set:
            raise ValueError("Необходимо указать хотя бы одно поле")
        return self


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    template_id: int | None
    style_id: int
    style_name: str
    teacher_id: int
    teacher_name: str
    substitute_teacher_id: int | None
    substitute_teacher_name: str | None
    event_date: datetime.date
    time_start: datetime.time
    duration_minutes: int
    max_students: int
    status: str
    enrolled_count: int


class EnrollmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    user_id: int

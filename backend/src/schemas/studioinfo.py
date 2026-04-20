from pydantic import BaseModel, EmailStr, Field

from src.core.constants import EMAIL_MAX_LENGTH, PHONE_MAX_LENGTH


class StudioInfoResponse(BaseModel):
    """Схема информации о студии для ответа API."""
    year_opened: int
    students_count: int
    phone: str | None = None
    address: str | None = None
    working_hours: str | None = None
    email: str | None = None


class StudioInfoUpdate(BaseModel):
    """Схема для обновления информации о студии."""
    year_opened: int | None = Field(None, ge=2000, le=2100)
    students_count: int | None = Field(None, ge=0)
    phone: str | None = Field(None, max_length=PHONE_MAX_LENGTH)
    address: str | None = None
    working_hours: str | None = None
    email: EmailStr | None = Field(None, max_length=EMAIL_MAX_LENGTH)

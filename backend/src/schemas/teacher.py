from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.core.constants import (
    DESCRIPTION_MAX_LENGTH,
    DESCRIPTION_MIN_LENGTH,
    IMAGE_URL_MAX_LENGTH,
    IMAGE_URL_MIN_LENGTH,
    NAME_MAX_LENGTH,
    NAME_MIN_LENGTH,
)


class TeacherPhotoCreate(BaseModel):
    """Схема для загрузки фото преподавателя."""
    url: str = Field(
        min_length=IMAGE_URL_MIN_LENGTH,
        max_length=IMAGE_URL_MAX_LENGTH
    )
    sort_order: int = Field(default=1, ge=1)


class TeacherPhotoUpdate(BaseModel):
    """Схема для обновления sort_order фото."""
    sort_order: int = Field(ge=1)


class TeacherPhotoResponse(BaseModel):
    """Схема фото преподавателя для ответа API."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    sort_order: int


class TeacherResponse(BaseModel):
    """Схема преподавателя для ответа API."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    bio: str | None
    is_active: bool
    sort_order: int = 1
    photos: list[TeacherPhotoResponse] = Field(default_factory=list)


class TeacherReorderItem(BaseModel):
    id: int
    sort_order: int = Field(ge=1)


class TeacherCreate(BaseModel):
    """
    Схема для создания преподавателя.
    При создании поле is_active=false (на уровне БД).
    """
    name: str = Field(
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH
    )
    bio: str | None = Field(
        default=None,
        min_length=DESCRIPTION_MIN_LENGTH,
        max_length=DESCRIPTION_MAX_LENGTH
    )


class TeacherUpdate(BaseModel):
    """Схема для обновления полей у преподавателя."""
    name: str | None = Field(
        default=None,
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH
    )
    bio: str | None = Field(
        default=None,
        min_length=DESCRIPTION_MIN_LENGTH,
        max_length=DESCRIPTION_MAX_LENGTH
    )
    is_active: bool | None = Field(default=None)

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "TeacherUpdate":
        if self.name is None and self.bio is None and self.is_active is None:
            raise ValueError("Необходимо указать хотя бы одно поле")
        return self

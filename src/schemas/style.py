from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.core.constants import (
    STYLE_DESCRIPTION_MAX_LENGTH,
    STYLE_DESCRIPTION_MIN_LENGTH,
    STYLE_IMAGE_URL_MAX_LENGTH,
    STYLE_IMAGE_URL_MIN_LENGTH,
    STYLE_NAME_MAX_LENGTH,
    STYLE_NAME_MIN_LENGTH,
)


class StyleImageCreate(BaseModel):
    """Схема для загрузки изображения стиля."""
    url: str = Field(
        min_length=STYLE_IMAGE_URL_MIN_LENGTH,
        max_length=STYLE_IMAGE_URL_MAX_LENGTH
    )
    sort_order: int = Field(default=1, ge=1)  # место в карусели фото.


class StyleImageResponse(BaseModel):
    """Схема изображения стиля для ответа API."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    sort_order: int


class StyleResponse(BaseModel):
    """Схема стиля танца для ответа API."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    is_active: bool
    images: list[StyleImageResponse] = Field(default_factory=list)


class StyleCreate(BaseModel):
    """
    Схема для создания стиля танца.
    При создании поле is_active=false (на уровне БД).
    """
    name: str = Field(
        min_length=STYLE_NAME_MIN_LENGTH,
        max_length=STYLE_NAME_MAX_LENGTH
    )
    description: str | None = Field(
        default=None,
        min_length=STYLE_DESCRIPTION_MIN_LENGTH,
        max_length=STYLE_DESCRIPTION_MAX_LENGTH
    )


class StyleUpdate(BaseModel):
    """Схема для обновления полей у стиля танца."""
    name: str | None = Field(
        default=None,
        min_length=STYLE_NAME_MIN_LENGTH,
        max_length=STYLE_NAME_MAX_LENGTH
    )
    description: str | None = Field(
        default=None,
        min_length=STYLE_DESCRIPTION_MIN_LENGTH,
        max_length=STYLE_DESCRIPTION_MAX_LENGTH
    )
    is_active: bool | None = Field(default=None)

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "StyleUpdate":
        if (
            self.name is None
            and self.description is None
            and self.is_active is None
        ):
            raise ValueError("Необходимо указать хотя бы одно поле")
        return self

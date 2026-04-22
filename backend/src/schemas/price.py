from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.core.constants import (
    DESCRIPTION_MAX_LENGTH,
    DESCRIPTION_MIN_LENGTH,
    NAME_MAX_LENGTH,
    NAME_MIN_LENGTH,
    OPTION_TEXT_MAX_LENGTH,
    PRICE_SUBTITLE_MAX_LENGTH,
)


class PricePlanOptionCreate(BaseModel):
    """Схема пункта списка включённого в тариф."""
    text: str = Field(min_length=1, max_length=OPTION_TEXT_MAX_LENGTH)
    sort_order: int = Field(default=1, ge=1)


class PricePlanOptionUpdate(BaseModel):
    sort_order: int = Field(ge=1)


class PricePlanOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    sort_order: int


class PricePlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: int
    subtitle: str | None
    is_active: bool
    is_recommended: bool
    sort_order: int
    options: list[PricePlanOptionResponse] = Field(default_factory=list)


class PricePlanCreate(BaseModel):
    name: str = Field(min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)
    description: str | None = Field(
        default=None,
        min_length=DESCRIPTION_MIN_LENGTH,
        max_length=DESCRIPTION_MAX_LENGTH,
    )
    price: int = Field(ge=0)
    subtitle: str | None = Field(
        default=None, max_length=PRICE_SUBTITLE_MAX_LENGTH
    )
    sort_order: int = Field(default=1, ge=1)


class PricePlanUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH,
    )
    description: str | None = Field(
        default=None,
        min_length=DESCRIPTION_MIN_LENGTH,
        max_length=DESCRIPTION_MAX_LENGTH,
    )
    price: int | None = Field(default=None, ge=0)
    subtitle: str | None = Field(
        default=None, max_length=PRICE_SUBTITLE_MAX_LENGTH
    )
    is_active: bool | None = Field(default=None)
    is_recommended: bool | None = Field(default=None)
    sort_order: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "PricePlanUpdate":
        if all(v is None for v in (
            self.name, self.description, self.price,
            self.subtitle, self.is_active, self.is_recommended, self.sort_order,
        )):
            raise ValueError("Необходимо указать хотя бы одно поле")
        return self

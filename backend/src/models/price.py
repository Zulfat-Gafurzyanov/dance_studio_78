from sqlalchemy import BigInteger, Boolean, false, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.constants import (
    DESCRIPTION_MAX_LENGTH,
    NAME_MAX_LENGTH,
    OPTION_TEXT_MAX_LENGTH,
    PRICE_SUBTITLE_MAX_LENGTH,
)
from src.db.base import Base


class PricePlanOption(Base):
    __tablename__ = "priceplanoption"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    text: Mapped[str] = mapped_column(String(OPTION_TEXT_MAX_LENGTH))
    sort_order: Mapped[int] = mapped_column(default=1)
    plan_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("priceplan.id", ondelete="CASCADE"),
        index=True,
    )


class PricePlan(Base):
    __tablename__ = "priceplan"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(
        String(NAME_MAX_LENGTH), nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        String(DESCRIPTION_MAX_LENGTH)
    )
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    subtitle: Mapped[str | None] = mapped_column(
        String(PRICE_SUBTITLE_MAX_LENGTH)
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=false(), nullable=False
    )
    is_recommended: Mapped[bool] = mapped_column(
        Boolean, server_default=false(), nullable=False
    )
    sort_order: Mapped[int] = mapped_column(default=1)

from sqlalchemy import BigInteger, Boolean, false, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.constants import (
    STYLE_DESCRIPTION_MAX_LENGTH,
    STYLE_IMAGE_URL_MAX_LENGTH,
    STYLE_NAME_MAX_LENGTH,
)
from src.db.base import Base


class StyleImage(Base):
    """Модель для хранения информации об изображении стиля."""
    __tablename__ = "imagestyle"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)

    url: Mapped[str] = mapped_column(String(STYLE_IMAGE_URL_MAX_LENGTH))
    sort_order: Mapped[int] = mapped_column(default=1)
    style_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("style.id", ondelete="CASCADE"),
        index=True
    )


class Style(Base):
    """Модель для хранения информации о стиле танца."""
    __tablename__ = "style"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(STYLE_NAME_MAX_LENGTH), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(
        String(STYLE_DESCRIPTION_MAX_LENGTH))
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=false(), nullable=False)

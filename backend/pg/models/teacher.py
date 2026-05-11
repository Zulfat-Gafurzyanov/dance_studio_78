from sqlalchemy import BigInteger, Boolean, false, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.constants import (
    DESCRIPTION_MAX_LENGTH,
    IMAGE_URL_MAX_LENGTH,
    NAME_MAX_LENGTH,
)
from src.db.base import Base


class TeacherPhoto(Base):
    """Модель для хранения фото преподавателя."""
    __tablename__ = "phototeacher"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True)

    url: Mapped[str] = mapped_column(String(IMAGE_URL_MAX_LENGTH))
    sort_order: Mapped[int] = mapped_column(default=1)
    teacher_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("teacher.id", ondelete="CASCADE"),
        index=True
    )


class Teacher(Base):
    """Модель для хранения информации о преподавателе."""
    __tablename__ = "teacher"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(
        String(NAME_MAX_LENGTH), unique=True, nullable=False
    )
    bio: Mapped[str | None] = mapped_column(
        String(DESCRIPTION_MAX_LENGTH)
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=false(), nullable=False
    )
    sort_order: Mapped[int] = mapped_column(default=1, server_default="1")

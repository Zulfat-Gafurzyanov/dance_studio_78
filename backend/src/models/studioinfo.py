from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.constants import EMAIL_MAX_LENGTH, PHONE_MAX_LENGTH
from src.db.base import Base


class StudioInfo(Base):
    __tablename__ = "studioinfo"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    year_opened: Mapped[int] = mapped_column(
        Integer, nullable=False, default=2020
    )
    students_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    phone: Mapped[str | None] = mapped_column(
        String(PHONE_MAX_LENGTH), nullable=True
    )
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    working_hours: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(
        String(EMAIL_MAX_LENGTH), nullable=True
    )

import datetime
import enum

from sqlalchemy import (
    BigInteger, Boolean, Date, Enum, ForeignKey, SmallInteger, Time, true
)
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base, TimestampMixin


class EventStatus(enum.Enum):
    SCHEDULED = "запланировано"
    CANCELLED = "отменено"


class ScheduleTemplate(Base, TimestampMixin):
    """
    Шаблон регулярного занятия — описывает повторяющееся расписание
    без привязки к конкретной дате.
    """

    __tablename__ = "schedule_template"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    style_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("style.id", ondelete="RESTRICT")
    )
    teacher_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("teacher.id", ondelete="RESTRICT")
    )
    day_of_week: Mapped[int] = mapped_column(SmallInteger)
    time_start: Mapped[datetime.time] = mapped_column(Time)
    duration_minutes: Mapped[int] = mapped_column(
        SmallInteger, server_default="60"
    )
    max_students: Mapped[int] = mapped_column(
        SmallInteger, server_default="8")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())


class ScheduleEvent(Base, TimestampMixin):
    """
    Конкретное занятие в расписании.
    Может быть создано из шаблона или вручную.
    """

    __tablename__ = "schedule_event"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    template_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("schedule_template.id", ondelete="SET NULL"),
        nullable=True
    )
    style_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("style.id", ondelete="RESTRICT")
    )
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("teacher.id", ondelete="RESTRICT")
    )
    substitute_teacher_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("teacher.id", ondelete="SET NULL"),
        nullable=True
    )
    event_date: Mapped[datetime.date] = mapped_column(Date)
    time_start: Mapped[datetime.time] = mapped_column(Time)
    duration_minutes: Mapped[int] = mapped_column(
        SmallInteger, server_default="60"
    )
    max_students: Mapped[int] = mapped_column(
        SmallInteger, server_default="8"
    )
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, values_callable=lambda x: [e.value for e in x]),
        default=EventStatus.SCHEDULED
    )


class Enrollment(Base, TimestampMixin):
    """Запись ученика на конкретное занятие."""

    __tablename__ = "enrollment"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE")
    )
    event_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("schedule_event.id", ondelete="CASCADE")
    )

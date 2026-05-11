import datetime

import asyncpg

from src.repository.base import BaseRepository


class ScheduleRepository(BaseRepository):

    # ===== Templates =====

    async def get_all_templates(self) -> list[asyncpg.Record]:
        return await self.fetch_all(
            """
            SELECT
                t.id, t.style_id, s.name AS style_name,
                t.teacher_id, te.name AS teacher_name,
                t.day_of_week, t.time_start, t.duration_minutes,
                t.max_students, t.is_active
            FROM schedule_template t
            JOIN style s ON s.id = t.style_id
            JOIN teacher te ON te.id = t.teacher_id
            ORDER BY t.day_of_week, t.time_start
            """
        )

    async def get_template_by_id(self, template_id: int) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            SELECT
                t.id, t.style_id, s.name AS style_name,
                t.teacher_id, te.name AS teacher_name,
                t.day_of_week, t.time_start, t.duration_minutes,
                t.max_students, t.is_active
            FROM schedule_template t
            JOIN style s ON s.id = t.style_id
            JOIN teacher te ON te.id = t.teacher_id
            WHERE t.id = $1
            """,
            template_id
        )

    async def create_template(
        self,
        style_id: int,
        teacher_id: int,
        day_of_week: int,
        time_start: datetime.time,
        duration_minutes: int,
        max_students: int,
    ) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            INSERT INTO schedule_template
                (style_id, teacher_id, day_of_week, time_start,
                 duration_minutes, max_students)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """,
            style_id, teacher_id, day_of_week, time_start,
            duration_minutes, max_students,
        )

    async def update_template(self, template_id: int, fields: dict) -> asyncpg.Record | None:
        set_clause = ", ".join(
            f"{key} = ${i}" for i, key in enumerate(fields.keys(), start=1)
        )
        values = list(fields.values()) + [template_id]
        return await self.fetch_row(
            f"UPDATE schedule_template SET {set_clause} WHERE id = ${len(values)} RETURNING id",
            *values,
        )

    async def delete_template(self, template_id: int) -> asyncpg.Record | None:
        return await self.fetch_row(
            "DELETE FROM schedule_template WHERE id = $1 RETURNING id",
            template_id,
        )

    # ===== Events =====

    async def get_events_by_date_range(
        self, date_from: datetime.date, date_to: datetime.date
    ) -> list[asyncpg.Record]:
        return await self.fetch_all(
            """
            SELECT
                e.id, e.template_id,
                e.style_id, s.name AS style_name,
                e.teacher_id, te.name AS teacher_name,
                e.substitute_teacher_id,
                sub.name AS substitute_teacher_name,
                e.event_date, e.time_start, e.duration_minutes,
                e.max_students, e.status,
                COUNT(en.id)::int AS enrolled_count
            FROM schedule_event e
            JOIN style s ON s.id = e.style_id
            JOIN teacher te ON te.id = e.teacher_id
            LEFT JOIN teacher sub ON sub.id = e.substitute_teacher_id
            LEFT JOIN enrollment en ON en.event_id = e.id
            WHERE e.event_date BETWEEN $1 AND $2
            GROUP BY e.id, s.name, te.name, sub.name
            ORDER BY e.event_date, e.time_start
            """,
            date_from, date_to,
        )

    async def get_event_by_id(self, event_id: int) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            SELECT
                e.id, e.template_id,
                e.style_id, s.name AS style_name,
                e.teacher_id, te.name AS teacher_name,
                e.substitute_teacher_id,
                sub.name AS substitute_teacher_name,
                e.event_date, e.time_start, e.duration_minutes,
                e.max_students, e.status,
                COUNT(en.id)::int AS enrolled_count
            FROM schedule_event e
            JOIN style s ON s.id = e.style_id
            JOIN teacher te ON te.id = e.teacher_id
            LEFT JOIN teacher sub ON sub.id = e.substitute_teacher_id
            LEFT JOIN enrollment en ON en.event_id = e.id
            WHERE e.id = $1
            GROUP BY e.id, s.name, te.name, sub.name
            """,
            event_id,
        )

    async def create_event(
        self,
        style_id: int,
        teacher_id: int,
        event_date: datetime.date,
        time_start: datetime.time,
        duration_minutes: int,
        max_students: int,
        template_id: int | None,
    ) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            INSERT INTO schedule_event
                (style_id, teacher_id, event_date, time_start,
                 duration_minutes, max_students, template_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
            """,
            style_id, teacher_id, event_date, time_start,
            duration_minutes, max_students, template_id,
        )

    async def update_event(self, event_id: int, fields: dict) -> asyncpg.Record | None:
        set_clause = ", ".join(
            f"{key} = ${i}" for i, key in enumerate(fields.keys(), start=1)
        )
        values = list(fields.values()) + [event_id]
        return await self.fetch_row(
            f"UPDATE schedule_event SET {set_clause} WHERE id = ${len(values)} RETURNING id",
            *values,
        )

    async def delete_event(self, event_id: int) -> asyncpg.Record | None:
        return await self.fetch_row(
            "DELETE FROM schedule_event WHERE id = $1 RETURNING id",
            event_id,
        )

    # ===== Enrollments =====

    async def get_user_enrolled_event_ids(self, user_id: int) -> list[int]:
        rows = await self.fetch_all(
            "SELECT event_id FROM enrollment WHERE user_id = $1",
            user_id,
        )
        return [row["event_id"] for row in rows]

    async def get_user_enrollment(self, event_id: int, user_id: int) -> asyncpg.Record | None:
        return await self.fetch_row(
            "SELECT id FROM enrollment WHERE event_id = $1 AND user_id = $2",
            event_id, user_id,
        )

    async def enroll(self, event_id: int, user_id: int) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            INSERT INTO enrollment (event_id, user_id)
            VALUES ($1, $2)
            RETURNING id, event_id, user_id
            """,
            event_id, user_id,
        )

    async def cancel_enrollment(self, event_id: int, user_id: int) -> asyncpg.Record | None:
        return await self.fetch_row(
            "DELETE FROM enrollment WHERE event_id = $1 AND user_id = $2 RETURNING id",
            event_id, user_id,
        )

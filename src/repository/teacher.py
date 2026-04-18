import asyncpg

from src.repository.base import BaseRepository


class TeacherRepository(BaseRepository):
    """
    Teacher:
        get_all — список всех преподавателей
        get_by_id — один преподаватель по id
        create — создание преподавателя
        update — обновление полей
        delete — удаление

    Photo:
        get_all_photos — получить все фото преподавателя
        add_photo — добавить фото к преподавателю
        delete_photo — удалить фото
    """

    # ===== Teacher =====

    async def get_all(self) -> list[asyncpg.Record]:
        return await self.fetch_all(
            """
            SELECT
                teacher.id AS teacher_id,
                teacher.name, teacher.bio, teacher.is_active,
                phototeacher.id AS photo_id,
                phototeacher.url, phototeacher.sort_order
            FROM teacher
            LEFT JOIN phototeacher ON phototeacher.teacher_id = teacher.id
            ORDER BY teacher.id, phototeacher.sort_order
            """
        )

    async def get_by_id(self, teacher_id: int) -> list[asyncpg.Record]:
        return await self.fetch_all(
            """
            SELECT
                teacher.id AS teacher_id,
                teacher.name, teacher.bio, teacher.is_active,
                phototeacher.id AS photo_id,
                phototeacher.url, phototeacher.sort_order
            FROM teacher
            LEFT JOIN phototeacher ON phototeacher.teacher_id = teacher.id
            WHERE teacher.id = $1
            ORDER BY phototeacher.sort_order
            """,
            teacher_id
        )

    async def create(
            self, name: str, bio: str | None) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            INSERT INTO teacher (name, bio)
            VALUES ($1, $2)
            RETURNING id, name, bio, is_active
            """,
            name,
            bio
        )

    async def update(
            self, teacher_id: int, fields: dict) -> asyncpg.Record | None:
        set_clause = ", ".join(
            f"{key} = ${i}" for i, key in enumerate(fields.keys(), start=1)
        )
        values = list(fields.values()) + [teacher_id]
        return await self.fetch_row(
            f"""
            UPDATE teacher
            SET {set_clause}
            WHERE id = ${len(values)}
            RETURNING id, name, bio, is_active
            """,
            *values
        )

    async def delete(self, teacher_id: int) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            DELETE FROM teacher
            WHERE id = $1
            RETURNING id
            """,
            teacher_id
        )

    # ===== Photo =====

    async def get_all_photos(self, teacher_id: int) -> list[asyncpg.Record]:
        return await self.fetch_all(
            """
            SELECT id AS photo_id, url, sort_order
            FROM phototeacher
            WHERE teacher_id = $1
            ORDER BY sort_order
            """,
            teacher_id
        )

    async def add_photo(
            self, teacher_id: int, url: str, sort_order: int
            ) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            INSERT INTO phototeacher (teacher_id, url, sort_order)
            VALUES ($1, $2, $3)
            RETURNING id AS photo_id, url, sort_order
            """,
            teacher_id,
            url,
            sort_order
        )

    async def delete_photo(self, photo_id: int) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            DELETE FROM phototeacher
            WHERE id = $1
            RETURNING id
            """,
            photo_id
        )

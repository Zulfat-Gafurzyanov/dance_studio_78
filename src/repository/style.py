import asyncpg

from src.repository.base import BaseRepository


class StyleRepository(BaseRepository):
    """
    Style:
        get_all — список всех стилей
        get_by_id — один стиль по id
        create — создание стиля
        update — обновление полей
        delete — удаление

    Image:
        get_all_images — получить все изображения стиля
        add_image — добавить изображение к стилю
        delete_image — удалить изображение
    """

    # ===== Style =====

    async def get_all(self) -> list[asyncpg.Record]:
        return await self.fetch_all(
            """
            SELECT
                style.id AS style_id,
                style.name, style.description, style.is_active,
                imagestyle.id AS image_id,
                imagestyle.url, imagestyle.sort_order
            FROM style
            LEFT JOIN imagestyle ON imagestyle.style_id = style.id
            ORDER BY style.id, imagestyle.sort_order
            """
        )

    async def get_by_id(self, style_id: int) -> list[asyncpg.Record]:
        return await self.fetch_all(
            """
            SELECT
                style.id AS style_id,
                style.name, style.description, style.is_active,
                imagestyle.id AS image_id,
                imagestyle.url, imagestyle.sort_order
            FROM style
            LEFT JOIN imagestyle ON imagestyle.style_id = style.id
            WHERE style.id = $1
            ORDER BY imagestyle.sort_order
            """,
            style_id
        )

    async def create(
            self, name: str, description: str | None) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            INSERT INTO style (name, description)
            VALUES ($1, $2)
            RETURNING id, name, description, is_active
            """,
            name,
            description
        )

    async def update(
            self, style_id: int, fields: dict) -> asyncpg.Record | None:
        # Создаем часть запроса (пример: "name = $1, is_active = $2").
        set_clause = ", ".join(
            f"{key} = ${i}" for i, key in enumerate(fields.keys(), start=1)
        )
        # Создаем список переданных параметров (пример: ["Хип-хоп", True, 5]).
        values = list(fields.values()) + [style_id]
        return await self.fetch_row(
            f"""
            UPDATE style
            SET {set_clause}
            WHERE id = ${len(values)}
            RETURNING id, name, description, is_active
            """,
            *values
        )

    async def delete(self, style_id: int) -> str:
        return await self.execute(
            """
            DELETE FROM style
            WHERE id = $1
            """,
            style_id
        )

    # ===== Image =====

    async def get_all_images(self, style_id: int) -> list[asyncpg.Record]:
        return await self.fetch_all(
            """
            SELECT id AS image_id, url, sort_order
            FROM imagestyle
            WHERE style_id = $1
            ORDER BY sort_order
            """,
            style_id
        )

    async def add_image(
            self, style_id: int, url: str, sort_order: int
            ) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            INSERT INTO imagestyle (style_id, url, sort_order)
            VALUES ($1, $2, $3)
            RETURNING id AS image_id, url, sort_order
            """,
            style_id,
            url,
            sort_order
        )

    async def delete_image(self, image_id: int) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            DELETE FROM imagestyle
            WHERE id = $1
            RETURNING id
            """,
            image_id
        )

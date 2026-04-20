import asyncpg

from src.repository.base import BaseRepository


class StudioInfoRepository(BaseRepository):
    """
    StudioInfo (singleton, id = 1):
        get    — получить информацию о студии
        update — обновить поля студии
    """

    async def get(self) -> asyncpg.Record | None:
        return await self.fetch_row(
            "SELECT * FROM studioinfo WHERE id = 1"
        )

    async def update(self, fields: dict) -> asyncpg.Record | None:
        set_clause = ", ".join(
            f"{key} = ${i}"
            for i, key in enumerate(fields.keys(), start=1)
        )
        values = list(fields.values())
        return await self.fetch_row(
            f"""
            UPDATE studioinfo
            SET {set_clause}
            WHERE id = 1
            RETURNING *
            """,
            *values,
        )

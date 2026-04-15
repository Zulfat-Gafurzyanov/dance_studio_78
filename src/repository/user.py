import asyncpg

from src.repository.base import BaseRepository


class UserRepository(BaseRepository):
    async def create(self, email: str, password_hash: str) -> asyncpg.Record:
        return await self.fetch_row(
            """
            INSERT INTO "user" (email, password_hash)
            VALUES ($1, $2)
            RETURNING id, email, is_active, created_at
            """,
            email,
            password_hash,
        )

    async def get_by_id(self, user_id: int) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            SELECT id, email, is_active, created_at
            FROM "user"
            WHERE id = $1
            """,
            user_id,
        )

    async def get_by_email(self, email: str) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            SELECT id, email, password_hash, is_active, created_at
            FROM "user"
            WHERE email = $1
            """,
            email,
        )

    async def update_email(self, user_id: int, email: str) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            UPDATE "user"
            SET email = $2, updated_at = NOW()
            WHERE id = $1
            RETURNING id, email, is_active, created_at
            """,
            user_id,
            email,
        )

    async def delete(self, user_id: int) -> bool:
        result = await self.execute(
            """
            DELETE FROM "user"
            WHERE id = $1
            """,
            user_id,
        )
        return result == "DELETE 1"

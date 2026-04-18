import asyncpg


class BaseRepository:
    """Базовый репозиторий — обёртка над asyncpg-соединением с общими методами запросов."""

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def fetch_row(self, query: str, *args) -> asyncpg.Record | None:
        return await self.conn.fetchrow(query, *args)

    async def fetch_all(self, query: str, *args) -> list[asyncpg.Record]:
        return await self.conn.fetch(query, *args)

    async def fetch_val(self, query: str, *args):
        return await self.conn.fetchval(query, *args)

    async def execute(self, query: str, *args) -> str:
        return await self.conn.execute(query, *args)

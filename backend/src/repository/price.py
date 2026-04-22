import asyncpg

from src.repository.base import BaseRepository


class PriceRepository(BaseRepository):
    """
    PricePlan:
        get_all   — список всех тарифов
        get_by_id — один тариф по id
        create    — создание тарифа
        update    — обновление полей
        delete    — удаление

    Option:
        add_option    — добавить пункт к тарифу
        update_option — обновить sort_order пункта
        delete_option — удалить пункт
    """

    # ===== PricePlan =====

    async def get_all(self) -> list[asyncpg.Record]:
        return await self.fetch_all(
            """
            SELECT
                p.id AS plan_id,
                p.name, p.description, p.price, p.subtitle,
                p.is_active, p.is_recommended, p.sort_order,
                o.id AS option_id,
                o.text, o.sort_order AS option_sort_order
            FROM priceplan p
            LEFT JOIN priceplanoption o ON o.plan_id = p.id
            ORDER BY p.sort_order, p.id, o.sort_order
            """
        )

    async def get_by_id(self, plan_id: int) -> list[asyncpg.Record]:
        return await self.fetch_all(
            """
            SELECT
                p.id AS plan_id,
                p.name, p.description, p.price, p.subtitle,
                p.is_active, p.is_recommended, p.sort_order,
                o.id AS option_id,
                o.text, o.sort_order AS option_sort_order
            FROM priceplan p
            LEFT JOIN priceplanoption o ON o.plan_id = p.id
            WHERE p.id = $1
            ORDER BY o.sort_order
            """,
            plan_id,
        )

    async def create(
        self,
        name: str,
        description: str | None,
        price: int,
        subtitle: str | None,
        sort_order: int,
    ) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            INSERT INTO priceplan (
                name, description, price,
                subtitle, sort_order
            )
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, name, description, price, subtitle,
                      is_active, is_recommended, sort_order
            """,
            name,
            description,
            price,
            subtitle,
            sort_order,
        )

    async def update(
        self, plan_id: int, fields: dict
    ) -> asyncpg.Record | None:
        set_clause = ", ".join(
            f"{key} = ${i}" for i, key in enumerate(fields.keys(), start=1)
        )
        values = list(fields.values()) + [plan_id]
        return await self.fetch_row(
            f"""
            UPDATE priceplan
            SET {set_clause}
            WHERE id = ${len(values)}
            RETURNING id, name, description, price, subtitle,
                      is_active, is_recommended, sort_order
            """,
            *values,
        )

    async def delete(self, plan_id: int) -> asyncpg.Record | None:
        return await self.fetch_row(
            "DELETE FROM priceplan WHERE id = $1 RETURNING id",
            plan_id,
        )

    # ===== Option =====

    async def add_option(
        self, plan_id: int, text: str, sort_order: int
    ) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            INSERT INTO priceplanoption (plan_id, text, sort_order)
            VALUES ($1, $2, $3)
            RETURNING id AS option_id, text, sort_order
            """,
            plan_id,
            text,
            sort_order,
        )

    async def update_option(
        self, option_id: int, sort_order: int
    ) -> asyncpg.Record | None:
        return await self.fetch_row(
            """
            UPDATE priceplanoption
            SET sort_order = $1
            WHERE id = $2
            RETURNING id AS option_id, text, sort_order
            """,
            sort_order,
            option_id,
        )

    async def delete_option(self, option_id: int) -> asyncpg.Record | None:
        return await self.fetch_row(
            "DELETE FROM priceplanoption WHERE id = $1 RETURNING id",
            option_id,
        )

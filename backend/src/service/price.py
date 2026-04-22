from fastapi import HTTPException, status

from src.repository.price import PriceRepository
from src.schemas.price import (
    PricePlanCreate,
    PricePlanOptionCreate,
    PricePlanOptionResponse,
    PricePlanOptionUpdate,
    PricePlanResponse,
    PricePlanUpdate,
)


class PriceService:
    def __init__(self, repository: PriceRepository):
        self.repository = repository

    def _group_rows(self, rows) -> list[PricePlanResponse]:
        grouped: dict[int, PricePlanResponse] = {}
        for row in rows:
            plan_id = row["plan_id"]
            if plan_id not in grouped:
                grouped[plan_id] = PricePlanResponse(
                    id=plan_id,
                    name=row["name"],
                    description=row["description"],
                    price=row["price"],
                    subtitle=row["subtitle"],
                    is_active=row["is_active"],
                    is_recommended=row["is_recommended"],
                    sort_order=row["sort_order"],
                    options=[],
                )
            if row["option_id"] is not None:
                grouped[plan_id].options.append(
                    PricePlanOptionResponse(
                        id=row["option_id"],
                        text=row["text"],
                        sort_order=row["option_sort_order"],
                    )
                )
        return list(grouped.values())

    async def get_all(self) -> list[PricePlanResponse]:
        rows = await self.repository.get_all()
        return self._group_rows(rows)

    async def get_by_id(self, plan_id: int) -> PricePlanResponse:
        rows = await self.repository.get_by_id(plan_id)
        if not rows:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Тариф не найден")
        return self._group_rows(rows)[0]

    async def create(self, data: PricePlanCreate) -> PricePlanResponse:
        record = await self.repository.create(
            name=data.name,
            description=data.description,
            price=data.price,
            subtitle=data.subtitle,
            sort_order=data.sort_order,
        )
        if not record:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Ошибка при создании тарифа",
            )
        return PricePlanResponse(
            id=record["id"],
            name=record["name"],
            description=record["description"],
            price=record["price"],
            subtitle=record["subtitle"],
            is_active=record["is_active"],
            is_recommended=record["is_recommended"],
            sort_order=record["sort_order"],
            options=[],
        )

    async def update(
        self, plan_id: int, data: PricePlanUpdate
    ) -> PricePlanResponse:
        rows = await self.repository.get_by_id(plan_id)
        if not rows:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Тариф не найден")
        fields = data.model_dump(exclude_unset=True)
        await self.repository.update(plan_id, fields)
        rows = await self.repository.get_by_id(plan_id)
        return self._group_rows(rows)[0]

    async def delete(self, plan_id: int) -> None:
        rows = await self.repository.get_by_id(plan_id)
        if not rows:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Тариф не найден")
        await self.repository.delete(plan_id)

    # ===== Option =====

    async def add_option(
        self, plan_id: int, data: PricePlanOptionCreate
    ) -> PricePlanOptionResponse:
        rows = await self.repository.get_by_id(plan_id)
        if not rows:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Тариф не найден")
        record = await self.repository.add_option(
            plan_id=plan_id,
            text=data.text,
            sort_order=data.sort_order,
        )
        if not record:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Ошибка при добавлении пункта",
            )
        return PricePlanOptionResponse(
            id=record["option_id"],
            text=record["text"],
            sort_order=record["sort_order"],
        )

    async def update_option(
        self, option_id: int, data: PricePlanOptionUpdate
    ) -> PricePlanOptionResponse:
        record = await self.repository.update_option(
            option_id, data.sort_order)
        if not record:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Пункт не найден"
            )
        return PricePlanOptionResponse(
            id=record["option_id"],
            text=record["text"],
            sort_order=record["sort_order"],
        )

    async def delete_option(self, option_id: int) -> None:
        deleted = await self.repository.delete_option(option_id)
        if not deleted:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Пункт не найден"
            )

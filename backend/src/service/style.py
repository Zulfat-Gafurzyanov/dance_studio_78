from fastapi import HTTPException, status

from src.repository.style import StyleRepository
from src.schemas.style import (
    StyleCreate,
    StyleImageCreate,
    StyleImageResponse,
    StyleImageUpdate,
    StyleResponse,
    StyleUpdate,
)


class StyleService:
    def __init__(self, repository: StyleRepository):
        self.repository = repository

    def _group_rows(self, rows) -> list[StyleResponse]:
        """Собирает строки JOIN в StyleResponse с вложенными изображениями."""
        grouped: dict[int, StyleResponse] = {}
        for row in rows:
            style_id = row["style_id"]
            if style_id not in grouped:
                grouped[style_id] = StyleResponse(
                    id=style_id,
                    name=row["name"],
                    description=row["description"],
                    is_active=row["is_active"],
                    images=[],
                )
            if row["image_id"] is not None:
                grouped[style_id].images.append(
                    StyleImageResponse(
                        id=row["image_id"],
                        url=row["url"],
                        sort_order=row["sort_order"],
                    )
                )
        return list(grouped.values())

    async def get_all(self) -> list[StyleResponse]:
        rows = await self.repository.get_all()
        return self._group_rows(rows)

    async def get_by_id(self, style_id: int) -> StyleResponse:
        rows = await self.repository.get_by_id(style_id)
        if not rows:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Стиль не найден")
        return self._group_rows(rows)[0]

    async def create(self, data: StyleCreate) -> StyleResponse:
        record = await self.repository.create(
            name=data.name,
            description=data.description,
        )
        if not record:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Ошибка при создании стиля"
            )
        return StyleResponse(
            id=record["id"],
            name=record["name"],
            description=record["description"],
            is_active=record["is_active"],
            images=[],
        )

    async def update(self, style_id: int, data: StyleUpdate) -> StyleResponse:
        rows = await self.repository.get_by_id(style_id)
        if not rows:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Стиль не найден")
        fields = data.model_dump(exclude_none=True)
        await self.repository.update(style_id, fields)
        rows = await self.repository.get_by_id(style_id)
        return self._group_rows(rows)[0]

    async def delete(self, style_id: int) -> None:
        rows = await self.repository.get_by_id(style_id)
        if not rows:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Стиль не найден")
        await self.repository.delete(style_id)

    # ===== Image =====

    async def add_image(
            self, style_id: int, data: StyleImageCreate) -> StyleImageResponse:
        rows = await self.repository.get_by_id(style_id)
        if not rows:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Стиль не найден")
        record = await self.repository.add_image(
            style_id=style_id,
            url=data.url,
            sort_order=data.sort_order,
        )
        if not record:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Ошибка при добавлении изображения"
            )
        return StyleImageResponse(
            id=record["image_id"],
            url=record["url"],
            sort_order=record["sort_order"],
        )

    async def update_image(
            self, image_id: int, data: StyleImageUpdate) -> StyleImageResponse:
        record = await self.repository.update_image(image_id, data.sort_order)
        if not record:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Изображение не найдено")
        return StyleImageResponse(
            id=record["image_id"],
            url=record["url"],
            sort_order=record["sort_order"],
        )

    async def delete_image(self, image_id: int) -> None:
        deleted = await self.repository.delete_image(image_id)
        if not deleted:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Изображение не найдено")

from fastapi import HTTPException, status

from src.repository.teacher import TeacherRepository
from src.schemas.teacher import (
    TeacherCreate,
    TeacherPhotoCreate,
    TeacherPhotoResponse,
    TeacherResponse,
    TeacherUpdate,
)


class TeacherService:
    def __init__(self, repository: TeacherRepository):
        self.repository = repository

    def _group_rows(self, rows) -> list[TeacherResponse]:
        """Собирает строки JOIN в TeacherResponse с вложенными фото."""
        grouped: dict[int, TeacherResponse] = {}
        for row in rows:
            teacher_id = row["teacher_id"]
            if teacher_id not in grouped:
                grouped[teacher_id] = TeacherResponse(
                    id=teacher_id,
                    name=row["name"],
                    bio=row["bio"],
                    is_active=row["is_active"],
                    photos=[],
                )
            if row["photo_id"] is not None:
                grouped[teacher_id].photos.append(
                    TeacherPhotoResponse(
                        id=row["photo_id"],
                        url=row["url"],
                        sort_order=row["sort_order"],
                    )
                )
        return list(grouped.values())

    async def get_all(self) -> list[TeacherResponse]:
        rows = await self.repository.get_all()
        return self._group_rows(rows)

    async def get_by_id(self, teacher_id: int) -> TeacherResponse:
        rows = await self.repository.get_by_id(teacher_id)
        if not rows:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Преподаватель не найден"
            )
        return self._group_rows(rows)[0]

    async def create(self, data: TeacherCreate) -> TeacherResponse:
        record = await self.repository.create(
            name=data.name,
            bio=data.bio,
        )
        if not record:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Ошибка при создании преподавателя"
            )
        return TeacherResponse(
            id=record["id"],
            name=record["name"],
            bio=record["bio"],
            is_active=record["is_active"],
            photos=[],
        )

    async def update(
            self, teacher_id: int, data: TeacherUpdate) -> TeacherResponse:
        rows = await self.repository.get_by_id(teacher_id)
        if not rows:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Преподаватель не найден"
            )
        fields = data.model_dump(exclude_none=True)
        await self.repository.update(teacher_id, fields)
        rows = await self.repository.get_by_id(teacher_id)
        return self._group_rows(rows)[0]

    async def delete(self, teacher_id: int) -> None:
        rows = await self.repository.get_by_id(teacher_id)
        if not rows:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Преподаватель не найден"
            )
        await self.repository.delete(teacher_id)

    # ===== Photo =====

    async def add_photo(
            self,
            teacher_id: int,
            data: TeacherPhotoCreate) -> TeacherPhotoResponse:
        rows = await self.repository.get_by_id(teacher_id)
        if not rows:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Преподаватель не найден"
            )
        record = await self.repository.add_photo(
            teacher_id=teacher_id,
            url=data.url,
            sort_order=data.sort_order,
        )
        if not record:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Ошибка при добавлении фото"
            )
        return TeacherPhotoResponse(
            id=record["photo_id"],
            url=record["url"],
            sort_order=record["sort_order"],
        )

    async def delete_photo(self, photo_id: int) -> None:
        deleted = await self.repository.delete_photo(photo_id)
        if not deleted:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "Фото не найдено")
